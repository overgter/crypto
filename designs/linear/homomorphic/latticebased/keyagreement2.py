from crypto.utilities import random_integer, big_prime

A_SIZE = 32
B_SIZE = 32
X_SIZE = 32
Y_SIZE = 33
PRIVATE_KEY_SIZE = 32

def generate_parameters(a_size=A_SIZE, b_size=B_SIZE,
                        x_size=X_SIZE, y_size=Y_SIZE):
    a = random_integer(a_size)
    b = random_integer(b_size)
    x = random_integer(x_size)
    y = big_prime(y_size)
    return a, b, x, y

A, B, X, Y = generate_parameters()
    
def calculate_a_adjustment(point_count):
    #(0, 0) (1, 0) (2, 1) (3, 3) (4, 5), (5, 7)
    if point_count in (0, 1):
        return 0    
    return 1 + (2 * (point_count - 2)) 
        
# y - 1 = identity
# y - 2 = inverse
        
def point_addition(a, b, x, y, point_count):    
    _a = pow(a, point_count, y)
    adjustment = calculate_a_adjustment(point_count)
    return ((_a * x) + (b * y * (a + adjustment))) % y
    
def compute_inverse(a, b, x, y, point_count):
    return point_addition(a, b, x, y, y - (1 + point_count))    
        
def generate_private_key(private_key_size=PRIVATE_KEY_SIZE):
    return random_integer(private_key_size)        
    
def generate_public_key(private_key, a=A, b=B, x=X, y=Y):
    return point_addition(a, b, x, y, private_key)
    
def generate_keypair(private_key_size=PRIVATE_KEY_SIZE, parameters=(A, B, X, Y)):
    private_key = generate_private_key(private_key_size)
    public_key = generate_public_key(private_key, *parameters)
    return public_key, private_key
    
def key_agreement(public_key, private_key, a=A, b=B, y=Y):
    return point_addition(a, b, public_key, y, private_key)
        
def test_key_agreement():
    from unittesting import test_key_agreement
    test_key_agreement("keyagreement2", generate_keypair, key_agreement, iterations=10000)
    
def test_inverse():
    public1, private1 = generate_keypair() 
    a, b, x, y = A, B, X, Y
    _public1 = point_addition(a, b, x, y, private1)
    assert public1 == _public1    
    
    _x = compute_inverse(A, B, _public1, Y, private1)    
    assert _x == x, (_x, x)    
        
if __name__ == "__main__":
    test_key_agreement()
    test_inverse()
    