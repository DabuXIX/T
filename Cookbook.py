def generate_xbm_data(ttf_path, char_list, forced_height, max_width, canvas_width, canvas_height,
                      threshold_value=128, padding_top=0, padding_bottom=0):
    """
    Generates XBM data for characters, ensuring proper alignment within grids, narrow character handling, and padding.
    """
    font_size = forced_height * 2
    font = ImageFont.truetype(ttf_path, font_size)
    all_xbm_data = {}

    punctuation_set = {',', '.'}
    punctuation_scale = 0.25
    narrow_chars = {"I"}
    narrow_char_scale = 0.5

    grid_width = 17 if canvas_width == 32 and canvas_height == 64 else canvas_width
    grid_height = 39 if canvas_width == 32 and canvas_height == 64 else canvas_height

    for char in char_list:
        try:
            if char == " ":
                binary_array = np.zeros((grid_height, grid_width), dtype=np.uint8)
                padded_array = np.zeros((canvas_height, canvas_width), dtype=np.uint8)
                all_xbm_data[char] = padded_array
                continue

            (width, height), (offset_x, offset_y) = font.font.getsize(char)
            if width == 0 or height == 0:
                continue

            image = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(image)
            draw.text((-offset_x, -offset_y), char, font=font, fill=255)

            if char in punctuation_set:
                target_height = int(forced_height * punctuation_scale)
                aspect_ratio = width / height
                scaled_width = min(int(target_height * aspect_ratio), max_width)
            elif char in narrow_chars:
                target_height = forced_height
                aspect_ratio = width / height
                scaled_width = min(int(target_height * aspect_ratio * narrow_char_scale), max_width)
            else:
                target_height = forced_height
                aspect_ratio = width / height
                scaled_width = min(int(target_height * aspect_ratio), max_width)

            img_resized = image.resize((scaled_width, target_height), Image.Resampling.LANCZOS)
            binary_array = (np.array(img_resized) > threshold_value).astype(np.uint8)

            padded_array = np.zeros((canvas_height, canvas_width), dtype=np.uint8)

            if canvas_width == 32 and canvas_height == 64:
                vertical_offset = (grid_height - binary_array.shape[0]) // 2
                horizontal_offset = (grid_width - binary_array.shape[1]) // 2
                padded_array[vertical_offset:grid_height, horizontal_offset:grid_width] = binary_array
            else:
                vertical_start = padding_top
                horizontal_padding = (canvas_width - scaled_width) // 2
                padded_array[vertical_start:vertical_start + target_height,
                             horizontal_padding:horizontal_padding + scaled_width] = binary_array

            xbm_data = []
            for row in padded_array:
                row_bytes = []
                for byte_index in range(0, canvas_width, 8):
                    byte = 0
                    for bit_index in range(8):
                        col = byte_index + bit_index
                        if col < canvas_width and row[col]:
                            byte |= (1 << (7 - bit_index))
                    row_bytes.append(reverse_bits(byte))
                xbm_data.append(row_bytes)

            all_xbm_data[char] = xbm_data

        except Exception as e:
            print(f"Warning: Unable to process character '{char}'. Reason: {e}")

    return all_xbm_data

                        def write_xbm(all_xbm_data, output_file, canvas_width, canvas_height):
    """
    Writes XBM data to a file, including both normal and strikeout versions.
    """
    def add_strikeout(xbm_data, canvas_width, canvas_height):
        strikeout_data = []
        middle_row = canvas_height // 2
        for i, row_bytes in enumerate(xbm_data):
            new_row = row_bytes[:]
            if i == middle_row:
                new_row = [0xFF] * len(row_bytes)  # Full strikeout on middle row
            strikeout_data.append(new_row)
        return strikeout_data

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# XBM File\n\n")

        for char, xbm_data in all_xbm_data.items():
            strikeout_data = add_strikeout(xbm_data, canvas_width, canvas_height)

            # Normal character
            f.write(f"/* Character: '{char}' */\n")
            f.write(f"#define {char}_width {canvas_width}\n")
            f.write(f"#define {char}_height {canvas_height}\n")
            f.write(f"static char {char}_bits[] = {{\n")
            for row_bytes in xbm_data:
                f.write("  " + ", ".join(f"0x{byte:02X}" for byte in row_bytes) + ",\n")
            f.write("};\n\n")

            # Strikeout character
            f.write(f"/* Strikeout Character: '{char}' */\n")
            f.write(f"static char {char}_strikeout_bits[] = {{\n")
            for row_bytes in strikeout_data:
                f.write("  " + ", ".join(f"0x{byte:02X}" for byte in row_bytes) + ",\n")
            f.write("};\n\n")

    print(f"XBM file saved as {output_file}")
