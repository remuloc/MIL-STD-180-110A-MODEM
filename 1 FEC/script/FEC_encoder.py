
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================


from pathlib import Path

# ============================================================
# PATH CONFIGURATION
# ============================================================

from pathlib import Path

# Directory configuration
SCRIPT_DIR = Path(__file__).resolve().parent
FEC_DIR = SCRIPT_DIR.parent

INPUT_DIR = FEC_DIR / "input"
PYTHON_OUTPUT_DIR = FEC_DIR / "output_python"
GNURADIO_OUTPUT_DIR = FEC_DIR / "output_gnuradio"

# File configuration
INPUT_FILE = INPUT_DIR / "sequence_1101.bin"
PYTHON_OUTPUT_FILE = PYTHON_OUTPUT_DIR / "output_1101.bin"
GNURADIO_OUTPUT_FILE = GNURADIO_OUTPUT_DIR / "output_1101.bin"


# ============================================================
# FEC PARAMETERS
# ============================================================

K = 7
POLYS = [5, 6]

INITIAL_STATE = 0

# None = process all input bits
LIMIT_INPUT_BITS = None


# ============================================================
# READ INPUT MESSAGE
# ============================================================

def read_input_bits(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    data = file_path.read_bytes()

    bits = []

    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    if LIMIT_INPUT_BITS is not None:
        bits = bits[:LIMIT_INPUT_BITS]

    return bits


# ============================================================
# CONVOLUTIONAL FEC ENCODER
# ============================================================

def fec_encode(input_bits):

    state = INITIAL_STATE
    encoded_bits = []

    for bit in input_bits:

        state = ((state << 1) | bit) & ((1 << K) - 1)

        for polynomial in POLYS:

            parity = (state & polynomial).bit_count() % 2

            encoded_bits.append(parity)

    return encoded_bits


# ============================================================
# SAVE PYTHON ENCODED OUTPUT
# ============================================================

def save_encoded_bits(bits, file_path):

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(bytes(bits))


# ============================================================
# READ GNU RADIO OUTPUT
# ============================================================

def read_gnuradio_output(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"GNU Radio output not found: {file_path}"
        )

    data = file_path.read_bytes()

    if any(byte not in (0, 1) for byte in data):
        raise ValueError(
            "GNU Radio output must contain only bytes 0 and 1."
        )

    return list(data)


# ============================================================
# BIT-BY-BIT VALIDATION
# ============================================================

def compare_outputs(python_bits, gnuradio_bits):

    print("\n========== FEC VALIDATION ==========")

    common_length = min(
        len(python_bits),
        len(gnuradio_bits)
    )

    errors = []

    for i in range(common_length):

        if python_bits[i] != gnuradio_bits[i]:
            errors.append(i)

    print(f"Python output bits:    {len(python_bits)}")
    print(f"GNU Radio output bits: {len(gnuradio_bits)}")
    print(f"Compared bits:         {common_length}")
    print(f"Matching bits:         {common_length - len(errors)}")
    print(f"Mismatching bits:      {len(errors)}")

    if len(python_bits) != len(gnuradio_bits):
        print("\nWARNING: Output lengths are different.")

    if errors:

        print("\nValidation FAILED.")

        print("Error positions:")

        for position in errors:
            print(
                f"Position {position}: "
                f"Python={python_bits[position]}, "
                f"GNU Radio={gnuradio_bits[position]}"
            )

    elif len(python_bits) == len(gnuradio_bits):

        print("\nValidation PASSED.")
        print("Both encoded sequences are identical.")

    else:

        print("\nValidation FAILED.")
        print("The output lengths are different.")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("Reading original input message...")

    input_bits = read_input_bits(INPUT_FILE)

    print(f"Input bits: {len(input_bits)}")

    print("\nEncoding message using Python FEC encoder...")

    python_bits = fec_encode(input_bits)

    save_encoded_bits(
        python_bits,
        PYTHON_OUTPUT_FILE
    )

    print(f"Python output saved: {PYTHON_OUTPUT_FILE}")

    print("\nReading GNU Radio encoded output...")

    gnuradio_bits = read_gnuradio_output(
        GNURADIO_OUTPUT_FILE
    )

    print("\nComparing encoded sequences...")

    compare_outputs(
        python_bits,
        gnuradio_bits
    )


if __name__ == "__main__":
    main()
