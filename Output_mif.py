def write_all_bitmaps_to_file(mif_file, output_file, char_width=16, char_height=32):
    """
    Parse a MIF file and write all character bitmaps to a text file.

    Args:
        mif_file (str): Path to the MIF file.
        output_file (str): Path to the output text file.
        char_width (int): Width of the character in bits (e.g., 16 for 16x32 resolution).
        char_height (int): Height of the character in rows (e.g., 32 for 16x32 resolution).
    """
    def hex_to_binary(hex_value, width=8):
        """Convert a hex string to a binary string with fixed width."""
        return bin(int(hex_value, 16))[2:].zfill(width)

    try:
        with open(mif_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{mif_file}' not found!")
        return

    # Filter lines to ignore comments and empty lines
    content_lines = [
        line.strip()
        for line in lines
        if ":" in line and not line.strip().startswith("--")
    ]

    if not content_lines:
        print("No valid content lines found in the file.")
        return

    # Parse the MIF content into a dictionary of address -> data
    memory_map = {}
    for line in content_lines:
        try:
            address, data = line.split(":")
            data = data.strip().strip(";")  # Remove trailing semicolon
            memory_map[address.strip()] = data
        except ValueError as e:
            print(f"Error parsing line: {line}. Exception: {e}")
            continue

    # Sort addresses to process characters sequentially
    sorted_addresses = sorted(memory_map.keys(), key=lambda x: int(x, 16))

    # Open the output file
    with open(output_file, "w") as out_file:
        current_address = None
        current_bitmap = []
        for address in sorted_addresses:
            if current_address is None:
                current_address = address

            # Append the row to the current character's bitmap
            hex_value = memory_map[address]
            high_byte = hex_value[:2]  # First byte
            low_byte = hex_value[2:]   # Second byte
            binary_row = hex_to_binary(high_byte) + hex_to_binary(low_byte)
            current_bitmap.append(binary_row[:char_width])

            # If the character bitmap is complete, write it to the file
            if len(current_bitmap) == char_height:
                # Write the bitmap to the output file
                out_file.write(f"Character starting at address {current_address}:\n")
                for row in current_bitmap:
                    out_file.write("".join("#" if bit == "1" else "." for bit in row) + "\n")
                out_file.write("\n")  # Add a blank line between characters

                # Reset for the next character
                current_bitmap = []
                current_address = None

    print(f"All bitmaps written to {output_file}")
