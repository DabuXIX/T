def print_character_from_mif(mif_file, char_width=8, char_height=32, start_address=None):
    """
    Parse a MIF file and print a specific character as a bitmap to the terminal.

    Args:
        mif_file (str): Path to the MIF file.
        char_width (int): Width of the character in bits (8 for single-byte rows).
        char_height (int): Height of the character in rows (e.g., 32 rows).
        start_address (str): Hex address (e.g., '0000') of the character to display.
    """
    def hex_to_binary(hex_value, width):
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

    if start_address is None:
        print("Error: No starting address provided. Please specify a character address.")
        return

    # Retrieve the rows for the specified character
    current_address = int(start_address, 16)
    current_bitmap = []

    while len(current_bitmap) < char_height:
        address = f"{current_address:04X}"  # Format as 4-digit hex
        if address in memory_map:
            hex_value = memory_map[address]
            # Split the hex value into two bytes
            first_byte, second_byte = hex_value[:2], hex_value[2:]
            # Convert each byte to a binary row
            binary_row_1 = hex_to_binary(first_byte, char_width)
            binary_row_2 = hex_to_binary(second_byte, char_width)
            current_bitmap.extend([binary_row_1, binary_row_2])  # Add rows to bitmap
        else:
            print(f"Warning: Address {address} not found in the file.")
            current_bitmap.extend(["0" * char_width, "0" * char_width])  # Add empty rows
        current_address += 1

    # Trim the bitmap to the specified height
    current_bitmap = current_bitmap[:char_height]

    # Print the character bitmap
    print(f"=== Character at Address {start_address.upper()} ===")
    for row in current_bitmap:
        print("".join("#" if bit == "1" else "." for bit in row))
    print("\n--- End of Character ---\n")
