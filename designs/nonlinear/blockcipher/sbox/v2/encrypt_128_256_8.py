from os import urandom
import itertools

from crypto.utilities import xor_subroutine, rotate_left, rotate_right

KEY_SIZE = 32
WORDSIZE = 8
ROUNDS = 1

S_BOX = [11, 5, 4, 15, 12, 6, 9, 0, 13, 3, 14, 8, 1, 10, 2, 7]
S_BOX2 = [4, 10, 1, 6, 8, 15, 7, 12, 3, 0, 13, 14, 5, 9, 11, 2]
S_BOX256 = []
for byte in range(256):
    S_BOX256.append((S_BOX[byte >> 4] << 4) | S_BOX2[byte & 15])              
        
def add_key(a, b, c, d, key):    
    for index in range(4):
        a[index] ^= key[0 + index] 
        b[index] ^= key[4 + index] 
        c[index] ^= key[8 + index] 
        d[index] ^= key[12 + index]
            
def add_constants(a, b, c, d, round):
    for index in range(4):
        a[index] ^= S_BOX256[0 + index + round]    
        b[index] ^= S_BOX256[4 + index + round]
        c[index] ^= S_BOX256[8 + index + round]
        d[index] ^= S_BOX256[12 + index + round]
            
def mix_pair(top, bottom, wordsize=WORDSIZE):    
    top ^= bottom
    top = rotate_left(top, 1, wordsize)
    bottom ^= top
    bottom = rotate_left(bottom, 2, wordsize)
    top ^= bottom
    top = rotate_left(top, 4, wordsize)
    bottom ^= top            
    return top, bottom
    
def mix_pairs(a, b, c, d, wordsize=WORDSIZE):        
    for index in range(4):               
        a[index], b[index] = mix_pair(a[index], b[index], wordsize)        
        c[index], d[index] = mix_pair(c[index], d[index], wordsize)        
    
def shift_rows(b, d, amount, wordsize=WORDSIZE):
    # this does the equivalent of rotate(b, (amount * 8), wordsize=32)
    _b = b[:amount]
    del b[:amount]
    b.extend(_b)
    
    _d = d[:amount]
    del d[:amount]
    d.extend(_d)
                
def mix_state(a, b, c, d, wordsize=WORDSIZE):
    # a1 a2 a3 a4
    # b1 b2 b3 b4
    # c1 c2 c3 c4
    # d1 d2 d4 d4
    
    # mix pairs()
    
    # a1b1 a2b2 a3b3 a4b4
    # b1a1 b2a2 b3a3 b4a4 
               
    # c1d1 c2d2 c3d3 c4d4 
    # d1c1 d2c2 d3c3 d4c4 
    
    # shift rows(b, d, 1)
    
    # a1b1 a2b2 a3b3 a4b4
    # b2a2 b3a3 b4a4 b1a1 
               
    # c1d1 c2d2 c3d3 c4d4 
    # d2c2 d3c3 d4c4 d1c1 
    
    # mix pairs()
    
    # a1b1b2a2 a2b2b3a3 a3b3b4a4 a4b4b1a1
    # b2a2a1b1 b3a3a2b2 b4a4a3b3 b1a1a4b4
               
    # c1d1d2c2 c2d2d3c3 c3d3d4c4 c4d4d1c1
    # d2c2c1d1 d3c3c2d2 d4c4c3d3 d1c1c4d4
    
    # shift rows(b, d, 2)
    
    # a1b1b2a2 a2b2b3a3 a3b3b4a4 a4b4b1a1
    # b4a4a3b3 b1a1a4b4 b2a2a1b1 b3a3a2b2
               
    # c1d1d2c2 c2d2d3c3 c3d3d4c4 c4d4d1c1
    # d4c4c3d3 d1c1c4d4 d2c2c1d1 d3c3c2d2
    
    # mix pairs()    
    
    # a1b1b2a2b4a4a3b3 a2b2b3a3b1a1a4b4 a3b3b4a4b2a2a1b1 a4b4b1a1b3a3a2b2
    # b4a4a3b3a1b1b2a2 b1a1a4b4a2b2b3a3 b2a2a1b1a3b3b4a4 b3a3a2b2a4b4b1a1
               
    # c1d1d2c2d4c4c3d3 c2d2d3c3d1c1c4d4 c3d3d4c4d2c2c1d1 c4d4d1c1d3c3c2d2
    # d4c4c3d3c1d1d2c2 d1c1c4d4c2d2d3c3 d2c2c1d1c3d3d4c4 d3c3c2d2c4d4d1c1
    
    # mix the a row with the c row, and the b row with the d row 
    
    # a1b1b2a2b4a4a3b3c1d1d2c2d4c4c3d3 a2b2b3a3b1a1a4b4c2d2d3c3d1c1c4d4 a3b3b4a4b2a2a1b1c3d3d4c4d2c2c1d1 a4b4b1a1b3a3a2b2c4d4d1c1d3c3c2d2           
    # b4a4a3b3a1b1b2a2d4c4c3d3c1d1d2c2 b1a1a4b4a2b2b3a3d1c1c4d4c2d2d3c3 b2a2a1b1a3b3b4a4d2c2c1d1c3d3d4c4 b3a3a2b2a4b4b1a1d3c3c2d2c4d4d1c1
    
    # c1d1d2c2d4c4c3d3a1b1b2a2b4a4a3b3 c2d2d3c3d1c1c4d4a2b2b3a3b1a1a4b4 c3d3d4c4d2c2c1d1a3b3b4a4b2a2a1b1 c4d4d1c1d3c3c2d2a4b4b1a1b3a3a2b2
    # d4c4c3d3c1d1d2c2b4a4a3b3a1b1b2a2 d1c1c4d4c2d2d3c3b1a1a4b4a2b2b3a3 d2c2c1d1c3d3d4c4b2a2a1b1a3b3b4a4 d3c3c2d2c4d4d1c1b3a3a2b2a4b4b1a1

    mix_pairs(a, b, c, d, wordsize)
    shift_rows(b, d, 1, wordsize)    
    mix_pairs(a, b, c, d, wordsize)
    shift_rows(b, d, 2, wordsize)
    mix_pairs(a, b, c, d, wordsize) 
    mix_pairs(a, c, b, d, wordsize)
    
def sbox_layer(a, b, c, d):
    a[0] = S_BOX256[a[0]]; a[1] = S_BOX256[a[1]]; a[2] = S_BOX256[a[2]]; a[3] = S_BOX256[a[3]]
    b[0] = S_BOX256[b[0]]; b[1] = S_BOX256[b[1]]; b[2] = S_BOX256[b[2]]; b[3] = S_BOX256[b[3]]
    c[0] = S_BOX256[c[0]]; c[1] = S_BOX256[c[1]]; c[2] = S_BOX256[c[2]]; c[3] = S_BOX256[c[3]]
    d[0] = S_BOX256[d[0]]; d[1] = S_BOX256[d[1]]; d[2] = S_BOX256[d[2]]; d[3] = S_BOX256[d[3]]               
        
def shuffle_pair(top, bottom, key, index, wordsize=WORDSIZE):   
    # a ^ (k & (a ^ b))
    # b ^= a
    # b &= k
    # b ^= a
    
    t = bottom
    bottom ^= top
    bottom &= key[index]
    bottom ^= top    
    
    top ^= t
    top &= key[index]
    top ^= t
    top = rotate_left(top, 1, wordsize)
    
    t = top
    top ^= bottom
    top &= key[index + 1]
    top ^= bottom        
    
    bottom ^= t
    bottom &= key[index + 1]
    bottom ^= t
    bottom = rotate_left(bottom, 2, wordsize)
    
    t = bottom
    bottom ^= top
    bottom &= key[index + 2]
    bottom ^= top    
    
    top ^= t
    top &= key[index + 2]
    top ^= t
    top = rotate_left(top, 4, wordsize)
    
    t = top
    top ^= bottom    
    top &= key[index + 3]    
    top ^= bottom           
    
    bottom ^= t
    bottom &= key[index + 3]
    bottom ^= t
    return top, bottom
        
def shuffle_pairs(a, b, c, d, key, wordsize=WORDSIZE):    
    for index in range(4):                       
        a[index], b[index] = shuffle_pair(a[index], b[index], key, (index * 4), wordsize)        
        c[index], d[index] = shuffle_pair(c[index], d[index], key, (index * 4), wordsize)     
    
def keyed_bit_permutation(a, b, c, d, key, wordsize=WORDSIZE):          
    shuffle_pairs(a, b, c, d, key)
    shift_rows(b, d, 1, wordsize)
    shuffle_pairs(a, b, c, d, key)
    shift_rows(b, d, 2, wordsize)
    shuffle_pairs(a, b, c, d, key) 
    shuffle_pairs(a, c, b, d, key)                       
        
def encrypt(plaintext, key, wordsize=WORDSIZE, rounds=ROUNDS):      
    # 128 bit state    
    assert len(key) == KEY_SIZE
    assert isinstance(plaintext, bytearray)
    key2 = key[16:32]
    a, b, c, d = plaintext[:4], plaintext[4:8], plaintext[8:12], plaintext[12:16]   
    add_key(a, b, c, d, key)    
    for round in range(rounds):
        add_constants(a, b, c, d, round)        
        keyed_bit_permutation(a, b, c, d, key2)
        sbox_layer(a, b, c, d)       
        mix_state(a, b, c, d)                      
    add_key(a, b, c, d, key)
    plaintext[:] = a + b + c + d
    return plaintext
            
def generate_key():
    return bytearray(urandom(KEY_SIZE))
    
def test_encrypt():
    key = range(KEY_SIZE)     
    #key = bytearray(32)
    #key[0] = 1
    message = bytearray(range(16))
    message[0] = 1
    ciphertext = encrypt(message, key)[:]
    print ciphertext
    #plaintext = decrypt(message, key)
    #assert plaintext == message, (plaintext, message)
    
    message = bytearray(range(16))
    message[0] = 2
    ciphertext = encrypt(message, key)[:]
    print ciphertext
    #plaintext = decrypt(message, key)
    #assert plaintext == message, (plaintext, message)
    
              
def test_metrics():
    import crypto
    class Test_Cipher(crypto.Cipher):
                
                
        def __init__(self, *args):
            super(Test_Cipher, self).__init__(*args)
            self.blocksize = 16
            
        def encrypt_block(self, data, key, tag=None, tweak=None):        
            encrypt(data, key)      
            
    
    Test_Cipher.test_metrics(generate_key(), "\x00" * 16, avalanche_test=False, randomness_test=False, bias_test=False, period_test=False)

def test_active_bits():    
    from crypto.analysis.active_bits import search_minimum_active_bits
    from crypto.utilities import integer_to_bytes, bytes_to_integer
    
    def test_function(state):
        a, b, c, d = state        
        #sbox_layer(a, b, c, d)
        mix_state(a, b, c, d)               
        #sbox_layer(a, b, c, d)
        #mix_state(a, b, c, d)        
        #mix_state(a, b, c, d)
        #mix_state(a, b, c, d)        
        return a, b, c, d
        
    def argument_function(a, b, c, d):
        return integer_to_bytes(a, 4), integer_to_bytes(b, 4), integer_to_bytes(c, 4), integer_to_bytes(d, 4)                
        
    def output_function(state):
        return tuple(bytes_to_integer(section) for section in state)
    
    search_minimum_active_bits(test_function, argument_function, output_function)
    
if __name__ == "__main__":     
    test_encrypt()
    #test_active_bits()
    test_metrics()
    