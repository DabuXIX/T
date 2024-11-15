def write_binary(char_list, all_xbm_data, output_dir, default_height, smaller_height):
    # Define the data array for 8KB size (8192 bytes), initialized to zero
    dataArray = [0] * 8192
    
    # Section 1: Non-strikeout characters with default height, addresses 0x0000 to 0x07FF
    current_address = 0x0000
    for char in char_list[:2048 // default_height]:  # Adjust range for default height section
        sanitized_char = filename(char)
        xbm_data = all_xbm_data.get(sanitized_char, [0] * 16)[:16]  # Limit to 16 bytes
        for i, byte in enumerate(xbm_data):
            dataArray[current_address + i] = reverse_bits(byte)
        current_address += 16

    # Section 2: Strikeout characters with default height, addresses 0x0800 to 0x0FFF
    strikeout_start = 0x0800
    for char in char_list[:2048 // default_height]:
        sanitized_char = filename(char)
        strikeout_data = Strikeout(all_xbm_data.get(sanitized_char, [0] * 16))[:16]  # Limit to 16 bytes
        for i, byte in enumerate(strikeout_data):
            dataArray[strikeout_start + i] = reverse_bits(byte)
        strikeout_start += 16

    # Section 3: Non-strikeout characters with smaller height, addresses 0x1000 to 0x17FF
    current_address = 0x1000
    for char in char_list[:2048 // smaller_height]:  # Adjust range for smaller height section
        sanitized_char = filename(char)
        xbm_data = all_xbm_data.get(sanitized_char, [0] * 8)[:8]  # Limit to 8 bytes for smaller height
        for i, byte in enumerate(xbm_data):
            dataArray[current_address + i] = reverse_bits(byte)
        current_address += 8

    # Section 4: Strikeout characters with smaller height, addresses 0x1800 to 0x1FFF
    strikeout_start = 0x1800
    for char in char_list[:2048 // smaller_height]:
        sanitized_char = filename(char)
        strikeout_data = Strikeout(all_xbm_data.get(sanitized_char, [0] * 8))[:8]  # Limit to 8 bytes for smaller height
        for i, byte in enumerate(strikeout_data):
            dataArray[strikeout_start + i] = reverse_bits(byte)
        strikeout_start += 8

    # Write the full data array to a binary file
    binary_file_path = os.path.join(output_dir, f"FontRom_combined.bin")
    with open(binary_file_path, "wb") as bin_file:
        for byte in dataArray:
            bin_file.write(byte.to_bytes(1, 'big'))  # Write each byte in binary format

    print(f"Binary file saved as {binary_file_path}.")
