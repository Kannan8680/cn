def char_to_binary(c):
    """Convert a character to 8-bit binary string."""
    return format(ord(c), '08b')

def hamming_encode_4bits(data):
    """Encode 4-bit data using Hamming(7,4)"""
    d = [int(b) for b in data]
    # parity bits: p1, p2, p3
    p1 = (d[0] + d[1] + d[3]) % 2
    p2 = (d[0] + d[2] + d[3]) % 2
    p3 = (d[1] + d[2] + d[3]) % 2
    return [p1, p2, d[0], p3, d[1], d[2], d[3]]

def hamming_decode_7bits(bits):
    """Decode 7-bit Hamming code and correct single-bit error"""
    b = [int(x) for x in bits]
    # calculate syndrome
    s1 = (b[0] + b[2] + b[4] + b[6]) % 2
    s2 = (b[1] + b[2] + b[5] + b[6]) % 2
    s3 = (b[3] + b[4] + b[5] + b[6]) % 2
    error_pos = s1*1 + s2*2 + s3*4  # position of error (1-indexed)
    
    if error_pos != 0:
        print(f"Error detected at position {error_pos}, correcting...")
        b[error_pos-1] ^= 1  # correct the bit
    
    # extract original data bits: d1, d2, d3, d4
    data_bits = [b[2], b[4], b[5], b[6]]
    return ''.join(str(bit) for bit in data_bits)

def encode_word(word):
    """Encode entire word using Hamming(7,4)"""
    encoded_blocks = []
    for char in word:
        binary = char_to_binary(char)
        high, low = binary[:4], binary[4:]
        encoded_blocks.append(''.join(map(str, hamming_encode_4bits(high))))
        encoded_blocks.append(''.join(map(str, hamming_encode_4bits(low))))
    return encoded_blocks

def decode_word(encoded_blocks):
    """Decode list of 7-bit blocks back to original word"""
    binary_word = ''
    for block in encoded_blocks:
        binary_word += hamming_decode_7bits(block)
    # combine each 2 blocks into a char
    decoded_chars = []
    for i in range(0, len(binary_word), 8):
        byte = binary_word[i:i+8]
        decoded_chars.append(chr(int(byte, 2)))
    return ''.join(decoded_chars)

# -------- Example Usage --------
word = "HELLO"
encoded = encode_word(word)
print("Encoded Hamming blocks:")
print(encoded)

# Optional: Introduce a single-bit error for testing
encoded_with_error = encoded.copy()
encoded_with_error[2] = encoded_with_error[2][:3] + str(int(encoded_with_error[2][3])^1) + encoded_with_error[2][4:]
print("\nEncoded blocks with 1-bit error in block 3:")
print(encoded_with_error)

decoded = decode_word(encoded_with_error)
print("\nDecoded word after error correction:")
print(decoded)
