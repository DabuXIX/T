def generate_xbm_data(ttf_path, char_list, forced_height, max_width, canvas_width, canvas_height,
                      threshold_value=128, padding_top=0, padding_bottom=0):
    """
    Generates XBM data for characters, ensuring proper padding and alignment.
    Handles punctuation scaling (e.g., commas, periods) with bottom alignment.
    Adjusts for glyph offsets to ensure true left alignment.
    """
    font_size = forced_height * 2
    font = ImageFont.truetype(ttf_path, font_size)
    all_xbm_data = {}

    # Define punctuation characters and a scaling ratio
    punctuation_set = {',', '.'}
    punctuation_scale = 0.25  # Typically, punctuation is 25% of the height of regular characters

    for char in char_list:
        try:
            # Render the character
            (width, height), (offset_x, offset_y) = font.font.getsize(char)
            if width == 0 or height == 0:
                if char == " ":
                    width, height = max_width, forced_height
                else:
                    print(f"Warning: Character '{char}' has zero dimensions. Skipping.")
                    continue

            image = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(image)
            draw.text((-offset_x, -offset_y), char, font=font, fill=255)

            # Determine target height for punctuation or regular characters
            if char in punctuation_set:
                target_height = int(forced_height * punctuation_scale)
            else:
                target_height = forced_height

            # Scale character to fit max dimensions
            aspect_ratio = width / height
            scaled_width = min(int(target_height * aspect_ratio), max_width)
            img_resized = image.resize((scaled_width, target_height), Image.Resampling.LANCZOS)

            # Convert to binary array
            binary_array = (np.array(img_resized) > threshold_value).astype(np.uint8)

            # Create padded array
            padded_array = np.zeros((canvas_height, canvas_width), dtype=np.uint8)

            # Adjust vertical alignment
            if char in punctuation_set:
                # Align punctuation at the bottom of the canvas
                vertical_start = canvas_height - target_height - padding_bottom
            else:
                # Center vertically for regular characters
                vertical_start = padding_top

            # True left alignment for 32x64 canvas (adjust for glyph offsets)
            if canvas_width == 32 and canvas_height == 64:
                horizontal_padding = max(0, -offset_x)  # Adjust for negative offsets
            else:
                # Center horizontally for other sizes
                horizontal_padding = (canvas_width - scaled_width) // 2

            # Place character in padded array
            padded_array[vertical_start:vertical_start + target_height,
                         horizontal_padding:horizontal_padding + scaled_width] = binary_array

            # Convert each row to multiple bytes (32 bits = 4 bytes for larger canvas sizes)
            xbm_data = []
            for row in padded_array:
                row_bytes = []
                for byte_index in range(0, canvas_width, 8):  # Process 8 bits (1 byte) at a time
                    byte = 0
                    for bit_index in range(8):
                        col = byte_index + bit_index
                        if col < canvas_width and row[col]:
                            byte |= (1 << (7 - bit_index))
                    # Reverse bits for compatibility
                    row_bytes.append(reverse_bits(byte))
                xbm_data.append(row_bytes)

            all_xbm_data[char] = xbm_data

        except Exception as e:
            print(f"Warning: Unable to process character '{char}'. Reason: {e}")

    return all_xbm_data