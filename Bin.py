def write_binary(char_list, all_xbm_data, output_dir, short_height, normal_height):
    """
    Creates a single binary file combining data from two MIF files for short and normal heights.
    The binary file follows the layout:
    - 0x0000 - 0x07FF: Short height non-strikeout
    - 0x0800 - 0x0FFF: Short height strikeout
    - 0x1000 - 0x17FF: Normal height non-strikeout
    - 0x1800 - 0x1FFF: Normal height strikeout
    - The last two bytes (0x1FFE and 0x1FFF) are reserved for the checksum.
    """
    binary_file_path = os.path.join(output_dir, "FontRom_combined.bin")
    data_array = [0x00] * 8192  # Initialize array for 8KB binary file

    # Helper variables for binary sections
    sections = [
        (0x0000, 0x0800, short_height, "normal"),  # Short height non-strikeout
        (0x0800, 0x1000, short_height, "strikeout"),  # Short height strikeout
        (0x1000, 0x1800, normal_height, "normal"),  # Normal height non-strikeout
        (0x1800, 0x1FFF, normal_height, "strikeout")  # Normal height strikeout
    ]

    for start_addr, end_addr, height, variant in sections:
        current_address = start_addr
        for char in char_list:
            sanitized_char = filename(char)
            if sanitized_char not in all_xbm_data or len(all_xbm_data[sanitized_char]) != height * 2:
                continue

            # Get the data and apply strikeout if needed
            xbm_data = all_xbm_data[sanitized_char][:16]
            if variant == "strikeout":
                xbm_data = strikeout(xbm_data)

            # Write data to the binary array
            for i, byte in enumerate(xbm_data):
                data_array[current_address + i] = reverse_bits(byte)
            current_address += 16

            # Stop if we reach the section end address
            if current_address >= end_addr:
                break

    # Step 4: Calculate checksum over the first 8190 bytes (excluding the last two bytes reserved for checksum)
    checksum = sum(data_array[:-2]) & 0xFFFF  # Get the least significant 16 bits

    # Place the checksum in the last two bytes of data_array
    data_array[-2] = (checksum >> 8) & 0xFF  # High byte
    data_array[-1] = checksum & 0xFF         # Low byte

    # Step 5: Write to the binary file
    with open(binary_file_path, "wb") as bin_file:
        bin_file.write(bytearray(data_array))

    print(f"Binary file saved as {binary_file_path}")

# Example usage
output_dir = "path_to_output_directory"
char_list = [chr(i) for i in range(0x20, 0x7F)]  # Include printable ASCII characters
all_xbm_data = {}  # This should be populated with your character data as dictionaries
short_height = 13
normal_height = 14

write_binary(char_list, all_xbm_data, output_dir, short_height, normal_height)
