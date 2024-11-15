def write_mif(char_list, all_xbm_data, output_dir, depth=8192, width=8):
    """
    Writes all character data in the same MIF file with comments indicating each character's label, variant, and height.
    """
    file_name = os.path.join(output_dir, "FontRom_combined.mif")
    with open(file_name, "w", encoding="utf-8") as f:
        # Write MIF header
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {width};\n")
        f.write(f"ADDRESS_RADIX = HEX;\n")
        f.write(f"DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n\n")

        sections = [
            (0x000, "Normal Height 1", "normal", 13),
            (0x800, "Strikeout Height 1", "strikeout", 13),
            (0x1000, "Normal Height 2", "normal", 14),
            (0x1800, "Strikeout Height 2", "strikeout", 14)
        ]

        for start_address, label, variant, height in sections:
            current_address = start_address
            f.write(f"\n-- {label} --\n")

            for char in char_list:
                if char in all_xbm_data and variant in all_xbm_data[char]:
                    xbm_data = all_xbm_data[char][variant][:16]  # Limit to 16 bytes
                    f.write(f"\n-- Character '{char}' ({label}, Height {height}) --\n")
                    for i, byte in enumerate(xbm_data):
                        f.write(f"{current_address + i:03X} : {byte:02X};\n")
                    current_address += 16
                else:
                    f.write(f"\n-- Character '{char}' ({label}, Height {height}) --\n")
                    f.write(f"-- No data available for character '{char}' in this configuration --\n")

            # Check if we’ve filled the current section up to the end address
            end_address = start_address + 0x800
            while current_address < end_address:
                f.write(f"{current_address:03X} : 00;\n")  # Fill unused addresses with 0x00
                current_address += 1

        f.write("END;\n")

    print(f"MIF file with all characters saved as {file_name}")
