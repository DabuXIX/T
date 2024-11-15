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

def ttf_to_xbm_combined(ttf_path, char_list, forced_height_1, forced_height_2, max_width=7, threshold_value=128, 
                        output_file="output_combined.xbm", padding_top=0, bottom_padding_1=0, bottom_padding_2=0):
    font_size = max(forced_height_1, forced_height_2) * 2
    font = ImageFont.truetype(ttf_path, font_size)

    all_xbm_data = {}

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Combined XBM file with dual heights and strikeout versions, grouped by type\n\n")

        output_configurations = [
            (forced_height_1, bottom_padding_1, "normal"),
            (forced_height_1, bottom_padding_1, "strikeout"),
            (forced_height_2, bottom_padding_2, "normal"),
            (forced_height_2, bottom_padding_2, "strikeout"),
        ]
        
        for height, bottom_padding, variant_label in output_configurations:
            for char in char_list:
                (width, actual_height), (offset_x, offset_y) = font.font.getsize(char)
                
                if actual_height == 0 or width == 0:
                    if char == ' ':
                        width, actual_height = max_width, height
                    else:
                        print(f"Warning: Character '{char}' has zero height or width. Skipping.")
                        continue

                image = Image.new('L', (width, actual_height), 0)
                draw = ImageDraw.Draw(image)
                draw.text((-offset_x, -offset_y), char, font=font, fill=255)
                
                total_height = height + padding_top + bottom_padding
                aspect_ratio = image.width / image.height
                new_width = min(int(height * aspect_ratio), max_width)
                img_resized = image.resize((new_width, height), Image.Resampling.LANCZOS)

                resized_array = np.array(img_resized)
                binary_array = (resized_array > threshold_value).astype(np.uint8)

                padded_array = np.zeros((total_height, 8), dtype=np.uint8)
                start_col = (8 - new_width) // 2
                start_row = padding_top

                padded_array[start_row:start_row + height, start_col:start_col + new_width] = binary_array[:, :new_width]

                if variant_label == "strikeout":
                    padded_array = strikeout_data(padded_array.copy(), new_width)

                xbm_data = []
                for row in padded_array:
                    byte_value = 0
                    for col in range(8):
                        if row[col] > 0:
                            byte_value |= (1 << (7 - col))
                    xbm_data.append(reverse_bits(byte_value))

                if char not in all_xbm_data:
                    all_xbm_data[char] = {}
                all_xbm_data[char][variant_label] = xbm_data

                f.write(f"/* Character: '{char}', Height: {total_height}, Variant: {variant_label} */\n")
                f.write(f"#define {char}_width 8\n")
                f.write(f"#define {char}_height {total_height}\n")
                f.write(f"static char {char}_bits_height_{height}_{variant_label}[] = {{\n")
                
                for i, byte in enumerate(xbm_data):
                    f.write(f" 0x{byte:02X}")
                    if i < len(xbm_data) - 1:
                        f.write(",")
                    if (i + 1) % 12 == 0:
                        f.write("\n")
                    else:
                        f.write(" ")
                f.write("\n};\n\n")

                # Debugging information
                print(f"Processed character '{char}' with height {height} as {variant_label}, data length: {len(xbm_data)}")

    print(f"Combined XBM file saved as {output_file}")
    return all_xbm_data

def write_mif(char_list, all_xbm_data, output_dir, height, depth=4096, width=8):
    file_name = os.path.join(output_dir, f"FontRom_{height}.mif")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {width};\n")
        f.write(f"ADDRESS_RADIX = HEX;\n")
        f.write(f"DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n")

        current_address = 0x000
        strikeout_start = 0x800

        for char in char_list:
            if char in all_xbm_data and "normal" in all_xbm_data[char]:
                xbm_data = all_xbm_data[char]["normal"][:16]
                for i, byte in enumerate(xbm_data):
                    f.write(f"{current_address + i:03X} : {byte:02X};\n")
                current_address += 16
            else:
                print(f"Warning: No normal data for character '{char}' at height {height}")

        for char in char_list:
            if char in all_xbm_data and "strikeout" in all_xbm_data[char]:
                xbm_data = all_xbm_data[char]["strikeout"][:16]
                for i, byte in enumerate(xbm_data):
                    f.write(f"{strikeout_start + i:03X} : {byte:02X};\n")
                strikeout_start += 16
            else:
                print(f"Warning: No strikeout data for character '{char}' at height {height}")

        f.write("END;\n")
    print(f"MIF file saved as {file_name}")

# Example usage
ttf_path = "path_to_your_font.ttf"
char_list = [chr(i) for i in range(0x20, 0x7F)]
output_dir = "path_to_output_directory"
all_xbm_data = ttf_to_xbm_combined(ttf_path, char_list, 14, 13, output_file="combined.xbm")

write_mif(char_list, all_xbm_data, output_dir, 13)
write_mif(char_list, all_xbm_data, output_dir, 14)
