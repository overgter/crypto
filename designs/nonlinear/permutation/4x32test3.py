def rotate_left(a, amount, bit_width=32, mask=0xFFFFFFFF):
    return ((a << amount) | (a >> (bit_width - amount))) & mask
    
def choice(a, b, c):
    return c ^ (a & (b ^ c))

def invert(a, mask=0xFFFFFFFF):
    return (~a) & mask
    
def _permutation(a, b, c, d, rotations, mask=0xFFFFFFFF):  
    a = (a + b) & mask
    a ^= c;
    a = (a + d) & mask
    a = rotate_left(a, rotations)
    a ^= b
    a = (a + c) & mask
    a ^= d
    a = rotate_left(a, rotations);
    return a
    
def _permutation2(a, b, c, d):
    a ^= choice(b, c, d)
    a = rotate_left(a, 1)
    b ^= choice(c, d, a)
    b = rotate_left(b, 2)
    c ^= choice(d, a, b)
    c = rotate_left(c, 3)
    d ^= choice(a, b, c)
    d = rotate_left(d, 4) 
    return a, b, c, d
    
def choice_swap(a, b, c):
    _t = b
    b = choice(a, b, c)
    c = choice(a, c, _t)
    return b, c
    
def bit_permutation(a, b, c, d):
    b, c = choice_swap(a, b, c)
    b = rotate_left(b, 1)
    c = rotate_left(c, 2)
    c, d = choice_swap(b, c, d)    
    d = rotate_left(d, 4)
    d, a = choice_swap(c, d, a)
    a = rotate_left(a, 8)
   # a, b = choice_swap(d, a, b)
    return a, b, c, d
    
def _pipeline_friendly_permutation(a, b, c, d, rotations, mask=0xFFFFFFFF):
    a = (a + b) & mask
    a ^= c;
    a = rotate_left(a, rotations);
    a = (a + d) & mask
    a ^= b;
    a = rotate_left(a, rotations);
    a = (a + c) & mask
    a ^= d;
    return a
    
def _pipeline_friendly_permutation2(a, b, c, d, mask=0xFFFFFFFF):
    a += b
    a ^= d
    c += d
    c ^= b 
    a = rotate_left(a, 2)
    c = rotate_left(c, 4)     
    b += c
    b ^= a
    d += a
    d ^= c  
    b = rotate_left(b, 8)
    d = rotate_left(d, 16)     
    return a, b, c, d
    
def add_choice(a, b, c):
    return c + (a & (b ^ c))
    
def _pipeline_friendly_permutation3(a, b, c, d, mask=0xFFFFFFFF):    
    a = (a + (d ^ rotate_left(add_choice(b, c, d), 1)     )) & mask
    b = (b + (a ^ rotate_left(add_choice(c, d, a), 2 + 8) )) & mask
    c = (c + (b ^ rotate_left(add_choice(d, a, b), 3 + 16))) & mask
    d = (d + (c ^ rotate_left(add_choice(a, b, c), 4 + 24))) & mask
    return a, b, c, d
        
def _pipeline_friendly_permutation4(a, b, c, d, amount, mask=0xFFFFFFFF):  
    a = (a + b) & mask
    a = rotate_left(a, amount)
    a ^= c
    a = (a + d) & mask
    return a
    
def _pipeline_friendly_permutation5(a, b, c, d, mask=0xFFFFFFFF):
    a = (a + b) & mask
    c = (c + d) & mask
    a = rotate_left(a, 1)
    c = rotate_left(c, 3)
    b ^= c
    d ^= a
    b = rotate_left(b, 2)
    d = rotate_left(d, 4)    
    return a, b, c, d
    
def _pipeline_friendly_permutation6(a, b, c, d, amount1, amount2, mask=0xFFFFFFFF):
    a = (a + b) & mask
    c ^= d    
    return b, d, a, c
    
def choice_swap(a, b, c):
    #t = b
    #b = choice(a, b, c)
    #c = choice(a, c, t)
    t = b ^ c
    t &= a    
    b = t ^ b
    c = t ^ c
    return b, c
    
def bit_permutation2(a, b, c, d):
    a, b = choice_swap(c, a, b)
    b, c = choice_swap(d, b, c)
    c, d = choice_swap(a, c, d)   
    a = rotate_left(a, 1)
    b = rotate_left(b, 2)          
    c = rotate_left(c, 3)
    d = rotate_left(d, 4)
    return a, b, c, d
    
def _invxor_permutation(a, b, c, d, amount, mask=0xFFFFFFFF):
    a ^= b    
    a = invert(a)
    c ^= a
    a = rotate_left(a, amount)
    a ^= c    
    a ^= d
    a ^= (invert(a) << 1) & mask
    return a, b, c, d    
        
def adder_permutation(a, b, c, d, amount, mask=0xFFFFFFFF):
    a &= b
    b ^= c    
    d = rotate_left(d, amount)
    a ^= mask # invert
    c ^= d    
    
    return a, b, c, d
    
def inverter_permutation(a, b, c, d, amount, mask=0xFFFFFFFF):
  #  a = a ^ mask
    a, b = choice_swap(a, b, c)
    a = rotate_left(a, 1)    
    c, d = choice_swap(c, d, b)
    b = rotate_left(b, 2)
    a, c = choice_swap(a, c, d)
    c = rotate_left(c, 3)
    b, d = choice_swap(b, d, a)
    d = rotate_left(d, 4)
    return a, b, c, d
       
def strange_addition(a, b, c):
    c ^= (a & b) ^ 0xFFFFFFFF
    a ^= b
    return a, b, c
    
def strange_addition_permutation(a, b, c, d, amount):
    a, b, c = strange_addition(a, b, c)
    a ^= c
    a, d, b = strange_addition(a, d, b)
    a = rotate_left(a, amount)
    return a, b, c, d        
        
from choicebitwisepermutation import bit_permutation
            
def permutation(a, b, c, d):    
    #a = _pipeline_friendly_permutation(a, b, c, d, 2)  
    #b = _pipeline_friendly_permutation(b, c, d, a, 4)
    #c = _pipeline_friendly_permutation(c, d, a, b, 8)                  
    #d = _pipeline_friendly_permutation(d, a, b, c, 16)
    #a, b, c, d = bit_permutation(a, b, c, d)    
    #a = _pipeline_friendly_permutation4(a, b, c, d, 1) 
    #b = _pipeline_friendly_permutation4(b, c, d, a, 2) 
    #c = _pipeline_friendly_permutation4(c, d, a, b, 3)
    #d = _pipeline_friendly_permutation4(d, a, b, c, 4)     
   # b = rotate_left(b, 2 + 8)
   # c = rotate_left(c, 3 + 16)
   # d = rotate_left(d, 4 + 24)  
   # a ^= 0xFFFFFFFF
    for round in range(1):       
        
        #a = (a + (b ^ c ^ d)) & 0xFFFFFFFF
        #b = (b + (a ^ c ^ d)) & 0xFFFFFFFF
        #c = (c + (a ^ b ^ d)) & 0xFFFFFFFF
        #d = (d + (a ^ b ^ c)) & 0xFFFFFFFF
        #b, a = choice_swap(d, b, a)                        
        #d, c = choice_swap(b, d, c)
        #a, d = choice_swap(c, a, d)
        #c, b = choice_swap(a, c, b)        
        a = _pipeline_friendly_permutation4(a, b, c, d, 1)
        b = _pipeline_friendly_permutation4(b, c, d, a, 2)
        c = _pipeline_friendly_permutation4(c, d, a, b, 3)
        d = _pipeline_friendly_permutation4(d, a, b, c, 4)
        b = rotate_left(b, 8)
        c = rotate_left(c, 16) 
        d = rotate_left(d, 24)
        
        #a ^= 0xFFFFFFFF
        #a, b, c, d, _, _, _, _ = bit_permutation(a, b, c, d, d, c, b, d)
        
        
    #b, a = choice_swap(d, b, a)
    #d, c = choice_swap(b, d, c) 
    #a = rotate_left(a, 1)
    #b = rotate_left(b, 2)        
    #c = rotate_left(c, 3)
    #d = rotate_left(d, 4)     
    #a, d = choice_swap(c, a, d)
    #c, b = choice_swap(a, c, b)   
    #a = rotate_left(a, 2)
    #b = rotate_left(b, 8)
    #c = rotate_left(c, 16)
    #d = rotate_left(d, 24)         
    return a, b, c, d    
    
def test_permutation2_sbox():
    sbox = bytearray()
    for a in range(2):
        for b in range(2):
            for c in range(2):
                for d in range(2):
                    _a, _b, _c, _d = _permutation2(a, b, c, d)                                        
                    sbox.append(((a | (b << 1) | (c << 2) | (d << 3)) & 255))
                    
    from crypto.analysis.cryptanalysis import summarize_sbox    
    print [byte for byte in sbox]
    summarize_sbox(sbox)
    
def visualize_permutation():
    from crypto.analysis.visualization import test_4x32_function
    test_4x32_function(permutation, (0, 0, 0, 1))
    
def test_permutation_active_bits(): 
    from crypto.analysis.active_bits import search_minimum_active_bits, THOROUGH_TEST
    pass_function = lambda *args: args
    search_minimum_active_bits(lambda args: permutation(*args), pass_function, lambda *args: args[0])#, test_inputs=THOROUGH_TEST)
    
if __name__ == "__main__":
    visualize_permutation()
    test_permutation_active_bits()
    #test_permutation2_sbox()
    