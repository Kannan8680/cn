import random

# --- (7,4) Hamming Code Implementation ---

def encode_hamming(data_bits):
    """Encodes 4 data bits [d1, d2, d3, d4] into a 7-bit Hamming code [c7..c1]."""
    d1, d2, d3, d4 = data_bits

    # Parity calculations (Even Parity)
    p1 = d1 ^ d2 ^ d4  # P1 checks d1, d2, d4
    p2 = d1 ^ d3 ^ d4  # P2 checks d1, d3, d4
    p3 = d2 ^ d3 ^ d4  # P3 checks d2, d3, d4

    # Order: [P1, P2, d1, P3, d2, d3, d4]
    return [p1, p2, d1, p3, d2, d3, d4]


def decode_and_correct(received_code):
    """Detects and corrects a single-bit error in the 7-bit Hamming code."""
    c1, c2, c3, c4, c5, c6, c7 = received_code

    # Syndrome calculation (S1 S2 S3) = Recalculate parity checks
    s1 = c1 ^ c3 ^ c5 ^ c7  # Check 1
    s2 = c2 ^ c3 ^ c6 ^ c7  # Check 2
    s3 = c4 ^ c5 ^ c6 ^ c7  # Check 3

    # Error position (in decimal: 1,2,3...) = binary value of (S3 S2 S1)
    syndrome_str = f"{s3}{s2}{s1}"
    error_pos = int(syndrome_str, 2)

    corrected_code = list(received_code)
    status = ""

    if error_pos != 0:
        # If error exists, flip the bit at position 'error_pos'
        list_index_to_flip = 7 - error_pos
        corrected_code[list_index_to_flip] ^= 1
        status = f"Error detected at position {error_pos}. Bit corrected."
    else:
        status = "No error detected."

    return corrected_code, status, syndrome_str


# --- Test Run ---
if __name__ == "__main__":
    # Input data stream: 4 bits [d1, d2, d3, d4]
    data_stream = [1, 0, 1, 1]
    print("=== Hamming Code Test Run (7,4) ===")
    print(f"1. Original Data Stream (d1 d2 d3 d4): {''.join(map(str, data_stream))}")

    # Encoding
    encoded_code = encode_hamming(data_stream)
    encoded_str = ''.join(map(str, encoded_code))
    print(f"2. Encoded Hamming Code [P1, P2, d1, P3, d2, d3, d4]: {encoded_str}")

    # Randomly select a position (1 to 7) for the error
    error_pos = random.randint(1, 7)
    list_index_to_flip = 7 - error_pos

    received_with_error = list(encoded_code)
    received_with_error[list_index_to_flip] ^= 1
    received_str = ''.join(map(str, received_with_error))

    print(f"3. Transmitted Code (error intentionally introduced at position {error_pos}): {received_str}")

    # Detection and Correction
    corrected_code, status, syndrome_str = decode_and_correct(received_with_error)
    corrected_str = ''.join(map(str, corrected_code))
    print(f"4. Error Detection & Correction:\n   Syndrome: {syndrome_str}\n   Status: {status}\n   Corrected Code: {corrected_str}")

    # Verification
    extracted_data = [corrected_code[2], corrected_code[4], corrected_code[5], corrected_code[6]]
    print(f"5. Extracted Data Bits (d1 d2 d3 d4): {''.join(map(str, extracted_data))}")

    if extracted_data == data_stream:
        print("✅ SUCCESS: The corrected data matches the original data stream.")
    else:
        print("❌ FAILURE: Correction failed.")
