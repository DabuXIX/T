def run_conversion(ttf_path, output_dir, char_list, forced_height_1, forced_height_2, max_width, padding_top, bottom_padding_1, bottom_padding_2):
    """Run the full conversion process, including XBM, MIF, and BIN generation."""
    try:
        # Generate XBM data
        all_xbm_data = generate_xbm_data(
            ttf_path, char_list, 
            forced_height_1=forced_height_1, 
            forced_height_2=forced_height_2, 
            max_width=max_width, 
            padding_top=padding_top, 
            bottom_padding_1=bottom_padding_1, 
            bottom_padding_2=bottom_padding_2
        )
        
        # Write combined XBM file
        write_xbm(all_xbm_data, os.path.join(output_dir, "combined.xbm"), char_list)
        
        # Write MIF files for both forced heights
        write_mif(char_list, all_xbm_data, output_dir, forced_height_1)
        write_mif(char_list, all_xbm_data, output_dir, forced_height_2)
        
        # Write combined binary file
        write_bin(char_list, all_xbm_data, output_dir)
        
        messagebox.showinfo("Success", "Conversion completed successfully! All files generated.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion: {e}")




def run_conversion(ttf_path, output_dir, char_list, forced_height_1, forced_height_2, max_width, padding_top, bottom_padding_1, bottom_padding_2):
    """Run the full conversion process, gracefully handling missing characters."""
    try:
        all_xbm_data = generate_xbm_data(
            ttf_path, char_list, 
            forced_height_1=forced_height_1, 
            forced_height_2=forced_height_2, 
            max_width=max_width, 
            padding_top=padding_top, 
            bottom_padding_1=bottom_padding_1, 
            bottom_padding_2=bottom_padding_2
        )
        
        if not all_xbm_data:
            messagebox.showwarning("Warning", "No characters could be processed. Check your TTF file or parameters.")
            return

        write_xbm(all_xbm_data, os.path.join(output_dir, "combined.xbm"), char_list)
        write_mif(char_list, all_xbm_data, output_dir, forced_height_1)
        write_mif(char_list, all_xbm_data, output_dir, forced_height_2)
        write_bin(char_list, all_xbm_data, output_dir)
        
        messagebox.showinfo("Success", "Conversion completed successfully! Files generated for available characters.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during convrsion: {e}"




                             def generate_xbm_data(ttf_path, char_list, forced_height_1, forced_height_2, max_width=7, threshold_value=70,
                      padding_top=1, bottom_padding_1=1, bottom_padding_2=2, padding_side="center"):
    """
    Generates XBM data for a list of characters with dual heights and strikeout options.
    Handles missing characters gracefully and logs warnings instead of stopping.
    """
    font_size = max(forced_height_1, forced_height_2) * 2
    font = ImageFont.truetype(ttf_path, font_size)
    all_xbm_data = {}
    missing_characters = []  # Track missing characters
    period_set = {'.', ','}  # Characters to render at their natural height

    output_configurations = [
        (forced_height_1, padding_top, bottom_padding_1, "normal"),
        (forced_height_1, padding_top, bottom_padding_1, "strikeout"),
        (forced_height_2, padding_top, bottom_padding_2, "normal"),
        (forced_height_2, padding_top, bottom_padding_2, "strikeout"),
    ]

    for height, top_padding, bottom_padding, variant_label in output_configurations:
        for char in char_list:
            try:
                use_native_height = char in period_set
                (width, actual_height), (offset_x, offset_y) = font.font.getsize(char)

                if actual_height == 0 or width == 0:
                    if char == ' ':
                        width, actual_height = max_width, height
                    else:
                        raise ValueError(f"Character '{char}' rendered with zero dimensions.")

                image = Image.new('L', (width, actual_height), 0)
                draw = ImageDraw.Draw(image)
                draw.text((-offset_x, -offset_y), char, font=font, fill=255)

                if use_native_height:
                    img_resized = image
                else:
                    aspect_ratio = image.width / image.height
                    new_width = min(int(height * aspect_ratio), max_width)
                    img_resized = image.resize((new_width, height), Image.Resampling.LANCZOS)

                resized_array = np.array(img_resized)
                binary_array = (resized_array > threshold_value).astype(np.uint8)

                total_height = height + top_padding + bottom_padding
                padded_array = np.zeros((16, 8), dtype=np.uint8)

                if padding_side == "right":
                    start_col = 0
                elif padding_side == "left":
                    start_col = 8 - new_width
                else:
                    start_col = (8 - new_width) // 2

                start_row = top_padding
                if use_native_height:
                    bottom_row = padded_array.shape[0] - actual_height
                    padded_array[bottom_row:, start_col:start_col + width] = binary_array[:, :width]
                else:
                    padded_array[start_row:start_row + height, start_col:start_col + new_width] = binary_array[:, :new_width]

                if variant_label == "strikeout" and not use_native_height:
                    padded_array = strikeout_data(padded_array.copy(), new_width)

                xbm_data = []
                for row in padded_array:
                    byte_value = 0
                    for col in range(8):
                        if row[col] > 0:
                            byte_value |= (1 << (7 - col))
                    xbm_data.append(byte_value)

                if char not in all_xbm_data:
                    all_xbm_data[char] = {}
                all_xbm_data[char][f"{variant_label}_{height}"] = xbm_data

            except Exception as e:
                if char not in missing_characters:
                    missing_characters.append(char)
                print(f"Warning: Unable to process character '{char}'. Reason: {e}")

    if missing_characters:
        print("\nThe following characters were not in the TTF file or could not be rendered:")
        for char in missing_characters:
            print(f"- '{char}' (Unicode: {ord(char)})")

    return all_xbm_data
