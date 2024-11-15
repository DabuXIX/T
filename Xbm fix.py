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

def generate_xbm_data(ttf_path, char_list, forced_height_1, forced_height_2, max_width=7, threshold_value=128,
                      padding_top=1, bottom_padding_1=1, bottom_padding_2=2):
    """
    Generates XBM data for a list of characters with dual heights and strikeout options.
    Returns a dictionary `all_xbm_data` with characters and their normal and strikeout data for both heights.
    """
    font_size = max(forced_height_1, forced_height_2) * 2
    font = ImageFont.truetype(ttf_path, font_size)
    all_xbm_data = {}

    # Define configurations to process each height and variant
    output_configurations = [
        (forced_height_1, padding_top, bottom_padding_1, "normal"),
        (forced_height_1, padding_top, bottom_padding_1, "strikeout"),
        (forced_height_2, padding_top, bottom_padding_2, "normal"),
        (forced_height_2, padding_top, bottom_padding_2, "strikeout"),
    ]
    
    for height, top_padding, bottom_padding, variant_label in output_configurations:
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
            
            aspect_ratio = image.width / image.height
            new_width = min(int(height * aspect_ratio), max_width)
            img_resized = image.resize((new_width, height), Image.Resampling.LANCZOS)

            resized_array = np.array(img_resized)
            binary_array = (resized_array > threshold_value).astype(np.uint8)

            # Apply padding to create an 8x16 array
            total_height = height + top_padding + bottom_padding
            padded_array = np.zeros((16, 8), dtype=np.uint8)

            # Place the character data in the center with padding
            start_col = (8 - new_width) // 2
            start_row = top_padding
            padded_array[start_row:start_row + height, start_col:start_col + new_width] = binary_array[:, :new_width]

            # Apply strikeout if the variant is "strikeout"
            if variant_label == "strikeout":
                padded_array = strikeout_data(padded_array.copy(), new_width)

            # Convert padded array to xbm_data (byte values)
            xbm_data = []
            for row in padded_array:
                byte_value = 0
                for col in range(8):
                    if row[col] > 0:
                        byte_value |= (1 << (7 - col))
                xbm_data.append(reverse_bits(byte_value))

            # Store the data in all_xbm_data
            if char not in all_xbm_data:
                all_xbm_data[char] = {}
            all_xbm_data[char][variant_label] = xbm_data

            print(f"Generated data for character '{char}', Height: {height}, Variant: {variant_label}, Data Length: {len(xbm_data)}")

    return all_xbm_data

def write_xbm(all_xbm_data, output_file):
    """ Writes all character data to a combined XBM file. """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Combined XBM file with dual heights and strikeout versions, grouped by type\n\n")

        for char, variants in all_xbm_data.items():
            for variant_label, xbm_data in variants.items():
                f.write(f"/* Character: '{char}', Variant: {variant_label} */\n")
                f.write(f"#define {char}_width 8\n")
                f.write(f"#define {char}_height {len(xbm_data)}\n")
                f.write(f"static char {char}_{variant_label}_bits[] = {{\n")
                
                for i, byte in enumerate(xbm_data):
                    f.write(f" 0x{byte:02X}")
                    if i < len(xbm_data) - 1:
                        f.write(",")
                    if (i + 1) % 12 == 0:
                        f.write("\n")
                    else:
                        f.write(" ")
                f.write("\n};\n\n")

    print(f"XBM file saved as {output_file}")

# Example usage
ttf_path = "path_to_your_font.ttf"
char_list = [chr(i) for i in range(0x20, 0x7F)]
output_dir = "path_to_output_directory"
output_file = "combined.xbm"

# Generate data with specified padding and size restrictions
all_xbm_data = generate_xbm_data(ttf_path, char_list, forced_height_1=14, forced_height_2=13, max_width=7,
                                 padding_top=1, bottom_padding_1=1, bottom_padding_2=2)

# Write XBM
write_xbm(all_xbm_data, output_file)
