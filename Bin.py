import os

def write_mif(char_list, all_xbm_data, output_dir, height, depth=4096, width=8):
    """
    Creates a MIF file for a specified character height.
    The first half of the file contains non-strikeout characters, and the second half contains strikeout characters.
    """
    file_name = os.path.join(output_dir, f"FontRom_{height}.mif")
    with open(file_name, "w", encoding="utf-8") as f:
        # Write the MIF header
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {width};\n")
        f.write(f"ADDRESS_RADIX = HEX;\n")
        f.write(f"DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n")

        current_address = 0x000
        strikeout_start = 0x800

        # Part 1: Write non-strikeout character data within the first 2048 addresses
        for char in char_list:
            if char not in all_xbm_data or len(all_xbm_data[char]) != height * 2:
                continue  # Skip characters that do not match the height or are missing

            xbm_data = all_xbm_data[char]["normal"][:16]  # Limit to 16 bytes for non-strikeout data
            f.write(f"\n-- Character: '{char}' at Address {current_address:03X} --\n")
            for i, byte in enumerate(xbm_data):
                f.write(f"{current_address + i:03X} : {reverse_bits(byte):02X};\n")
            current_address += 16

        # Part 2: Write strikeout character data within the next 2048 addresses (starting at 0x800)
        for char in char_list:
            if char not in all_xbm_data or len(all_xbm_data[char]) != height * 2:
                continue

            strikeout_data = all_xbm_data[char]["strikeout"][:16]  # Limit to 16 bytes for strikeout data
            f.write(f"\n-- Strikeout Character: '{char}' at Address {strikeout_start:03X} --\n")
            for i, byte in enumerate(strikeout_data):
                f.write(f"{strikeout_start + i:03X} : {reverse_bits(byte):02X};\n")
            strikeout_start += 16

        f.write("END;\n")

    print(f"MIF file saved as {file_name}")

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
            if char not in all_xbm_data or len(all_xbm_data[char]) != height * 2:
                continue

            # Get the data directly from all_xbm_data
            xbm_data = all_xbm_data[char][variant][:16]  # Limit to 16 bytes for each variant

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
all_xbm_data = {}  # This should be populated by `ttf_to_xbm_combined` with both "normal" and "strikeout" data
short_height = 13
normal_height = 14

write_mif(char_list, all_xbm_data, output_dir, short_height)
write_mif(char_list, all_xbm_data, output_dir, normal_height)
write_binary(char_list, all_xbm_data, output_dir, short_height, normal_height)
