def write_mif(char_list, all_xbm_data, output_dir, height, depth=4096, width=8):
    """
    Writes the data for each character to a separate MIF file for the specified height.
    Includes both normal and strikeout characters in the same file.
    """
    file_name = os.path.join(output_dir, f"FontRom_{height}.mif")
    with open(file_name, "w", encoding="utf-8") as f:
        # MIF header
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {width};\n")
        f.write(f"ADDRESS_RADIX = HEX;\n")
        f.write(f"DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n\n")

        current_address = 0x000
        strikeout_start = 0x0800

        # Write normal character data with comments
        f.write(f"-- Normal characters for height {height}\n")
        for char in char_list:
            label = f"normal_{height}"
            if label in all_xbm_data[char]:
                xbm_data = all_xbm_data[char][label]
                
                # Add a comment for the character
                f.write(f"-- Character: '{char}'\n")
                for i, byte in enumerate(xbm_data):
                    f.write(f"{current_address + i:04X} : {byte:02X};\n")
                current_address += 16  # Increment address by 16 bytes per character

        # Write strikeout character data with comments
        f.write(f"\n-- Strikeout characters for height {height}\n")
        for char in char_list:
            label = f"strikeout_{height}"
            if label in all_xbm_data[char]:
                xbm_data = all_xbm_data[char][label]
                
                # Add a comment for the character
                f.write(f"-- Character: '{char}'\n")
                for i, byte in enumerate(xbm_data):
                    f.write(f"{strikeout_start + i:04X} : {byte:02X};\n")
                strikeout_start += 16  # Increment address by 16 bytes per character

        # MIF footer
        f.write("\nEND;\n")
    print(f"MIF file saved as {file_name}")


# Generate data
ttf_path = "path_to_your_font.ttf"
char_list = [chr(i) for i in range(0x20, 0x7F)]
output_dir = "path_to_output_directory"
all_xbm_data = generate_xbm_data(ttf_path, char_list, forced_height_1=14, forced_height_2=13, max_width=7,
                                 padding_top=1, bottom_padding_1=1, bottom_padding_2=2)

# Write separate MIF files for each height
write_mif(char_list, all_xbm_data, output_dir, 13)
write_mif(char_list, all_xbm_data, output_dir, 14)
