def print_characters_from_mif_16x32(mif_file, char_width=16, char_height=32):
    """
    Parse a MIF file and print each 16x32 character as a bitmap to the terminal.

    Args:
        mif_file (str): Path to the MIF file.
        char_width (int): Width of the character in bits (16 for 16x32 resolution).
        char_height (int): Height of the character in rows (32 for 16x32 resolution).
    """
    def hex_to_binary(hex_value, width):
        """Convert a hex string to a binary string with fixed width."""
        return bin(int(hex_value, 16))[2:].zfill(width)

    with open(mif_file, "r") as f:
        lines = f.readlines()

    # Extract relevant lines (skip header and footer)
    content_lines = [line.strip() for line in lines if ":" in line]

    current_bitmap = []
    print("=== Parsed Characters ===")

    for line in content_lines:
        # Split the line into address and data
        address, data = line.split(":")
        hex_values = data.strip().split(" ")

        # Convert the hex values to a binary row (16 bits per row)
        binary_row = "".join(hex_to_binary(hex_value, 8) for hex_value in hex_values)
        current_bitmap.append(binary_row[:char_width])  # Trim to character width (16 bits)

        # If we have collected enough rows for one character, display it
        if len(current_bitmap) == char_height:
            # Print the character bitmap
            for row in current_bitmap:
                print("".join("#" if bit == "1" else "." for bit in row))
            print("\n--- End of Character ---\n")
            current_bitmap = []  # Reset for the next character
