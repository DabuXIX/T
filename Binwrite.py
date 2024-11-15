def write_mif_two_files(char_list, all_xbm_data, output_dir, default_height, smaller_height, depth=4096, width=8):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define file names for the two .mif files
    file_name_1 = os.path.join(output_dir, f"FontRom_{default_height}_part1.mif")
    file_name_2 = os.path.join(output_dir, f"FontRom_{smaller_height}_part2.mif")

    # Open both files for writing
    with open(file_name_1, "w", encoding="utf-8") as f1, open(file_name_2, "w", encoding="utf-8") as f2:
        # Write headers for both files
        for f, height in [(f1, default_height), (f2, smaller_height)]:
            f.write(f"DEPTH = {depth};\n")
            f.write(f"WIDTH = {width};\n")
            f.write(f"ADDRESS_RADIX = HEX;\n")
            f.write(f"DATA_RADIX = HEX;\n")
            f.write("CONTENT\nBEGIN\n")

        # Section 1: Non-strikeout for default height
        current_address = 0x0000
        for char in char_list[:2048 // default_height]:  # Adjust range for default height section
            sanitized_char = filename(char)
            xbm_data = all_xbm_data.get(sanitized_char, [0] * 16)[:16]  # Limit to 16 bytes
            f1.write(f"\n-- Character: '{char}' at Address {current_address:03X}\n")
            for byte in xbm_data:
                reversed_byte = reverse_bits(byte)
                f1.write(f"{current_address:03X} : {reversed_byte:02X};\n")
                current_address += 1

        # Section 2: Strikeout for default height
        strikeout_start = 0x0800
        for char in char_list[:2048 // default_height]:
            sanitized_char = filename(char)
            strikeout_data = Strikeout(all_xbm_data.get(sanitized_char, [0] * 16))[:16]
            f1.write(f"\n-- Strikeout Character: '{char}' at Address {strikeout_start:03X}\n")
            for byte in strikeout_data:
                reversed_byte = reverse_bits(byte)
                f1.write(f"{strikeout_start:03X} : {reversed_byte:02X};\n")
                strikeout_start += 1

        # Section 3: Non-strikeout for smaller height
        current_address = 0x1000
        for char in char_list[:2048 // smaller_height]:
            sanitized_char = filename(char)
            xbm_data = all_xbm_data.get(sanitized_char, [0] * 8)[:8]  # Limit to 8 bytes for smaller height
            f2.write(f"\n-- Character: '{char}' at Address {current_address:03X}\n")
            for byte in xbm_data:
                reversed_byte = reverse_bits(byte)
                f2.write(f"{current_address:03X} : {reversed_byte:02X};\n")
                current_address += 1

        # Section 4: Strikeout for smaller height
        strikeout_start = 0x1800
        for char in char_list[:2048 // smaller_height]:
            sanitized_char = filename(char)
            strikeout_data = Strikeout(all_xbm_data.get(sanitized_char, [0] * 8))[:8]
            f2.write(f"\n-- Strikeout Character: '{char}' at Address {strikeout_start:03X}\n")
            for byte in strikeout_data:
                reversed_byte = reverse_bits(byte)
                f2.write(f"{strikeout_start:03X} : {reversed_byte:02X};\n")
                strikeout_start += 1

        # End .mif content
        for f in (f1, f2):
            f.write("END;\n")

    print(f"MIF files saved as {file_name_1} and {file_name_2}.")
