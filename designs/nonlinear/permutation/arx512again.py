
class Register(object):
    
    def __init__(self, words, word_size=32, mask=0xFFFFFFFF):
        self.words = list(words)
        self.word_size = word_size
        self.mask = mask
        
    def __add__(self, other_words):
        words = self.words
        mask = self.mask
        for index, word in enumerate(other_words.words):
            words[index] = (words[index] + word) & mask
        return self
        
    def __xor__(self, other_words):
        words = self.words
        for index, word in enumerate(other_words.words):
            words[index] = words[index] ^ word
        return self
    
    def __mul__(self, other_words):
        mask = self.mask
        words = self.words
        for index, word in enumerate(other_words.words):
            words[index] = (words[index] * word) % mask
        return self
        
    def big_swap(self):        
        self.words = list(reversed(self.words))
                    
    def shift_rows(self, amount):
        self.words = self.words[amount:] + self.words[:amount]
        
    def shift_left(self, amount):
        mask = self.mask
        words = self.words
        for index, word in enumerate(words):
            words[index] = (word << amount) & mask
            
        
def mix_columns(a, b, c, d, constant=Register((2147483649, 1677216, 65537, 257))):    
    a += b           #   ab
    c += d        
    b ^= c
    d ^= a
    a *= constant      
    #c *= constant

    #a ^= c
    #b ^= d
    #c ^= b
    #d ^= a
    return a, b, c, d
          
def shift_rows(a, b, c, d, word_size=32):
    pass
    
def permutation(a, b, c, d, 
                e, f, g, h,
                i, j, k, l,
                m, n, o, p,
                word_size=32, mask=0xFFFFFFFF, rounds=1):
    a = Register((a, b, c, d), word_size, mask)
    b = Register((e, f, g, h), word_size, mask)
    c = Register((i, j, k, l), word_size, mask)
    d = Register((m, n, o, p), word_size, mask)
    round_constant = Register((1, 1, 1, 1), word_size, mask)        
    _increment = Register((1, 1, 1, 1), word_size, mask)
    for round in range(1, rounds + 1):        
        #a = a + round_constant
        #round_constant += _increment
        a, b, c, d = mix_columns(a, b, c, d)
        #b.shift_left(1)
        #a, b, c, d = mix_columns(a, b, c, d)    
        #a.big_swap()        
        #b.shift_rows(1)
        #c.shift_rows(2)
        #d.shift_rows(3)
    return a.words + b.words + c.words + d.words
    
def visualize_permutation():
    from crypto.analysis.visualization import test_16x32_function
    state = ([0] * 15) + [1]
    test_16x32_function(permutation, state)
    
if __name__ == "__main__":
    visualize_permutation()
    