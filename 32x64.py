def write_mif_32x64(char_list, all_xbm_data, output_dir, default_height=64, depth=8192, width=32):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.join(output_dir, f"FontRom_{default_height}.mif")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {width};\n")  # 32 bits (4 bytes)
        f.write(f"ADDRESS_RADIX = HEX;\n")
        f.write(f"DATA_RADIX = HEX;\n")
        f.write(f"CONTENT BEGIN\n")

        current_address = 0x0000  # Start of non-strikeout section

        # ** Non-Strikeout Section **
        for char in char_list:
            sanitized_char = filename(char)
            xbm_data = all_xbm_data.get(sanitized_char, [0] * 256)  # 256 bytes (32x64 resolution)

            f.write(f"\n-- Non-Strikeout Character: '{char}' at Address {current_address:03X}\n")
            for row in range(64):  # 64 rows
                row_data = xbm_data[row * 4:(row + 1) * 4]  # 4 bytes per row
                reversed_data = [reverse_bits(byte) for byte in row_data]  # Reverse each byte
                combined_data = "".join(f"{byte:02X}" for byte in reversed_data)  # Combine into 32 bits
                f.write(f"{current_address:03X} : {combined_data};\n")
                current_address += 1  # Increment address for each row

        # Ensure alignment with strikeout section (start of strikeout at 0x800)
        strikeout_start = 0x800

        # ** Strikeout Section **
        for char in char_list:
            sanitized_char = filename(char)
            xbm_data = all_xbm_data.get(sanitized_char, [0] * 256)  # 256 bytes (32x64 resolution)

            # Initialize strikeout_data as a copy of xbm_data
            strikeout_data = xbm_data[:]
            if len(strikeout_data) < 256:
                strikeout_data.extend([0] * (256 - len(strikeout_data)))  # Ensure padding

            # Add a horizontal strike-through line in the middle (row 32)
            middle_row = 32
            for col in range(32):  # Add strike line across 32 columns
                byte_index = middle_row * 4 + col // 8  # Calculate byte index
                strikeout_data[byte_index] |= (1 << (7 - (col % 8)))  # Set bit for strike line

            f.write(f"\n-- Strikeout Character: '{char}' at Address {strikeout_start:03X}\n")
            for row in range(64):  # 64 rows
                row_data = strikeout_data[row * 4:(row + 1) * 4]  # 4 bytes per row
                reversed_data = [reverse_bits(byte) for byte in row_data]
                combined_data = "".join(f"{byte:02X}" for byte in reversed_data)  # Combine into 32 bits
                f.write(f"{strikeout_start:03X} : {combined_data};\n")
                strikeout_start += 1  # Increment address for each row

        f.write("END;\n")
    print(f"MIF file saved as {file_name}.")