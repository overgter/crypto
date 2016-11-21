from os import urandom

from crypto.utilities import bytes_to_words, words_to_bytes
from crypto.designs.ciphercomponents import choice, rotate_left, rotate_right

def new_key(wordcount=4, wordsize=4):
    return tuple(bytes_to_words(bytearray(urandom(wordcount * wordsize)), wordsize)) 

def choice_swap(a, b, k):
    t = a
    a = choice(k, a, b)
    b = choice(k, b, t)
    return a, b
    
def shuffle_columns(a, b, c, d, k0, k1, k2, k3):
    a, b = choice_swap(a, b, k0)      
    c, d = choice_swap(c, d, k1)

    c, b = choice_swap(c, b, k2)
    a, d = choice_swap(a, d, k3)
    return a, b, c, d
    
def bit_permutation128(inputs, key, wordsize=32): 
    a, b, c, d = inputs
    k0, k1, k2, k3 = key
    for round in range(1):              
        a, b, c, d = shuffle_columns(a, b, c, d, k0, k1, k2, k3)                
        b = rotate_left(b, 1, wordsize)
        c = rotate_left(c, 2, wordsize)
        d = rotate_left(d, 3, wordsize)               
        
        
        a, b, c, d = shuffle_columns(a, b, c, d, k0, k1, k2, k3)                
        b = rotate_left(b, 4, wordsize)
        c = rotate_left(c, 8, wordsize)
        d = rotate_left(d, 12, wordsize)                              
        
        
        a, b, c, d = shuffle_columns(a, b, c, d, k0, k1, k2, k3)                    
        b = rotate_left(b, 8, wordsize)
        c = rotate_left(c, 12, wordsize)
        d = rotate_left(d, 16, wordsize)        
        
        
        a, b, c, d = shuffle_columns(a, b, c, d, k0, k1, k2, k3)
        a, b, c, d = b, c, d, a     
    return a, b, c, d
    
def invert_shuffle_columns(a, b, c, d, k0, k1, k2, k3):
    a, d = choice_swap(a, d, k3)
    c, b = choice_swap(c, b, k2)
    c, d = choice_swap(c, d, k1)
    a, b = choice_swap(a, b, k0)
    return a, b, c, d       
        
def invert_bit_permutation128(inputs, key, wordsize=32):
    a, b, c, d = inputs
    k0, k1, k2, k3 = key
    for round in range(1):
        a, b, c, d = d, a, b, c
        a, b, c, d = invert_shuffle_columns(a, b, c, d, k0, k1, k2, k3)
        
        d = rotate_right(d, 16, wordsize)
        c = rotate_right(c, 12, wordsize)
        b = rotate_right(b, 8, wordsize)        
        a, b, c, d = invert_shuffle_columns(a, b, c, d, k0, k1, k2, k3)
        
        d = rotate_right(d, 12, wordsize)
        c = rotate_right(c, 8, wordsize)
        b = rotate_right(b, 4, wordsize)
        a, b, c, d = invert_shuffle_columns(a, b, c, d, k0, k1, k2, k3)
        
        d = rotate_right(d, 3, wordsize)
        c = rotate_right(c, 2, wordsize)
        b = rotate_right(b, 1, wordsize)
        a, b, c, d = invert_shuffle_columns(a, b, c, d, k0, k1, k2, k3)

    return a, b, c, d
      
def encrypt64(data, key):
    padding = new_key(2, 4) # generate 2 32-bit words
    inputs = tuple(bytes_to_words(bytearray(data), 4)) + padding
    return words_to_bytes(bit_permutation128(inputs, key), 4)
    
def decrypt64(data, key):
    output = invert_bit_permutation128(bytes_to_words(data, 4), key)
    return words_to_bytes(output, 4)[:8]
    
def test_encrypt64_decrypt64():
    data = "TestData"
    key = new_key(4, 4) # 4 32-bit words
    ciphertext = encrypt64(data, key)
    plaintext = decrypt64(ciphertext, key)
    assert plaintext == data, (plaintext, data)
    
    data2 = bytearray((3, 13, 28, 21, 19, 9, 21, 21))
    ciphertext2 = encrypt64(data2, key)
    
    ciphertextxor = bytearray((ciphertext[index] ^ ciphertext2[index] for index in range(len(ciphertext))))
    plaintextxor = decrypt64(ciphertextxor, key)
    assert plaintextxor == "WhoaWhat", plaintextxor            
    print "Encrypt64/Decrypt64 unit test pass"
        
def test_invert_shuffle_columns():
    inputs = (1, 2, 4, 8)
    key = (123, 456, 789, 101112)
    outputs = shuffle_columns(*inputs + key)
    _inputs = invert_shuffle_columns(*outputs + key)
    assert _inputs == inputs, (_inputs, inputs)
    print "Invert shuffle columns unit test pass"
    
def test_invert_bit_permutation():
    inputs = (1, 2, 4, 8)
    key = (123, 456, 789, 101112)
    output = bit_permutation128(inputs, key)
    _inputs = invert_bit_permutation128(output, key)
    #_print_bits(_inputs)
    assert _inputs == inputs, (_inputs, inputs)
    print "Invert bit permutation unit test pass"    
    
def _print_bits(*inputs):
    for _input in inputs:
        print '-' * 80
        print '\n'.join(format(word, 'b').zfill(32) for word in _input)
            
def test_homomorphic_property():
    input1 = (1, 2, 4, 8)
    input2 = (2, 4, 8, 16)
    key = new_key()
    ciphertext1 = bit_permutation128(input1, key)
    ciphertext2 = bit_permutation128(input2, key)
    
    ciphertextxor = tuple(ciphertext1[index] ^ ciphertext2[index] for index in range(len(ciphertext1)))
    plaintextxor = tuple(input1[index] ^ input2[index] for index in range(len(input1)))
    
    ciphertextand = tuple(ciphertext1[index] & ciphertext2[index] for index in range(len(ciphertext1)))
    plaintextand = tuple(input1[index] & input2[index] for index in range(len(input1)))
    
    decryptedxor = invert_bit_permutation128(ciphertextxor, key)
    decryptedand = invert_bit_permutation128(ciphertextand, key)
            
    input3 = (4, 8, 16, 32)
    ciphertext3 = bit_permutation128(input3, key)
    #_print_bits(decryptedxor, plaintextxor, input1, input2)
    assert decryptedxor == plaintextxor, (decryptedxor, plaintextxor, input1, input2)
    assert decryptedand == plaintextand, (decryptedand, plaintextand, input1, input2)
    print "Homomorphic unit test pass"
    
if __name__ == "__main__":
    test_invert_shuffle_columns()
    test_invert_bit_permutation()
    test_homomorphic_property()
    test_encrypt64_decrypt64()
    