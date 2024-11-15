from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def reverse_bits(byte):
    return int('{:08b}'.format(byte)[::-1], 2)

def strikeout_data(data, width):
    """ Adds a strikeout line across the 7th and 8th row of character data. """
    if len(data) >= 8:
        data[6] = 0xFF  # Add strikeout in the 7th row
        data[7] = 0xFF  # Add strikeout in the 8th row
    return data

# ... (other functions such as generate_xbm_data and write_xbm remain unchanged) ...

def write_mif(char_list, all_xbm_data, output_dir, height, depth=4096, width=8):
    """
    Writes the data for each character in the specified height (normal and strikeout variants)
    to a MIF file, with comments for each character entry.
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
        strikeout_start = 0x800

        # Write non-strikeout (normal) data with comments
        for char in char_list:
            if char in all_xbm_data and "normal" in all_xbm_data[char]:
                xbm_data = all_xbm_data[char]["normal"][:16]
                
                # Add a comment for the character
                f.write(f"-- Character: '{char}' (Normal Height: {height})\n")
                for i, byte in enumerate(xbm_data):
                    f.write(f"{current_address + i:03X} : {byte:02X};\n")
                current_address += 16

        # Write strikeout data with comments
        for char in char_list:
            if char in all_xbm_data and "strikeout" in all_xbm_data[char]:
                xbm_data = all_xbm_data[char]["strikeout"][:16]
                
                # Add a comment for the character with strikeout
                f.write(f"\n-- Character: '{char}' (Strikeout Height: {height})\n")
                for i, byte in enumerate(xbm_data):
                    f.write(f"{strikeout_start + i:03X} : {byte:02X};\n")
                strikeout_start += 16

        # MIF footer
        f.write("\nEND;\n")
    print(f"MIF file saved as {file_name}")

# Example usage
ttf_path = "path_to_your_font.ttf"
char_list = [chr(i) for i in range(0x20, 0x7F)]
output_dir = "path_to_output_directory"
output_file = "combined.xbm"

# Generate data
all_xbm_data = generate_xbm_data(ttf_path, char_list, 14, 13)

# Write XBM
write_xbm(all_xbm_data, output_file)

# Write separated MIF files for each height with comments for each character entry
write_mif(char_list, all_xbm_data, output_dir, 13)
write_mif(char_list, all_xbm_data, output_dir, 14)
