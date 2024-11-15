def write_bin(char_list, all_xbm_data, output_dir):
    """
    Creates a binary file combining all character data:
    - 13px height: Normal and Strikeout (0x0000 - 0x0FFF)
    - 14px height: Normal and Strikeout (0x1000 - 0x1FFF)
    - The last 2 bytes (0x1FFE, 0x1FFF) store a checksum.
    """
    binary_file_path = os.path.join(output_dir, "FontRom_combined.bin")
    data_array = [0x00] * 8192  # Initialize array for 8KB binary file

    # Define sections for binary file
    sections = {
        "normal_13": 0x0000,
        "strikeout_13": 0x0800,
        "normal_14": 0x1000,
        "strikeout_14": 0x1800,
    }

    # Populate the binary array
    for label, start_address in sections.items():
        current_address = start_address
        for char in char_list:
            if label in all_xbm_data[char]:
                xbm_data = all_xbm_data[char][label]
                
                # Write character data
                for i, byte in enumerate(xbm_data):
                    data_array[current_address + i] = byte
                current_address += 16  # Increment by 16 bytes per character

    # Compute checksum over the first 8190 bytes
    checksum = sum(data_array[:-2]) & 0xFFFF
    data_array[-2] = (checksum >> 8) & 0xFF  # High byte
    data_array[-1] = checksum & 0xFF         # Low byte

    # Write binary file
    with open(binary_file_path, "wb") as bin_file:
        bin_file.write(bytearray(data_array))

    print(f"Binary file saved as {binary_file_path}")
