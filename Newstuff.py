def write_xbm(char_list, all_xbm_data, output_dir, width, height, smaller_height):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define file names for different heights
    file_name_default = os.path.join(output_dir, "c_default_height.xbm")
    file_name_smaller = os.path.join(output_dir, "c_smaller_height.xbm")

    # Write default height characters to one XBM file
    with open(file_name_default, "w", encoding="utf-8") as f_default:
        for char in char_list[:2048 // height]:  # Adjust range for default height section
            sanitized_char = filename(char)
            xbm_data = all_xbm_data.get(sanitized_char, [0] * 16)[:16]  # Limit to 16 bytes
            f_default.write(f"#define {sanitized_char}_width {width}\n")
            f_default.write(f"#define {sanitized_char}_height {height}\n")
            f_default.write(f"static char {sanitized_char}_bits[] = {{\n")
            for i, byte in enumerate(xbm_data):
                f_default.write(f"0x{byte:02X}")
                if i < len(xbm_data) - 1:
                    f_default.write(", ")
                if (i + 1) % 12 == 0:
                    f_default.write("\n")
            f_default.write("};\n\n")

    # Write smaller height characters to another XBM file
    with open(file_name_smaller, "w", encoding="utf-8") as f_smaller:
        for char in char_list[:2048 // smaller_height]:  # Adjust range for smaller height section
            sanitized_char = filename(char)
            xbm_data = all_xbm_data.get(sanitized_char, [0] * 8)[:8]  # Limit to 8 bytes for smaller height
            f_smaller.write(f"#define {sanitized_char}_width {width}\n")
            f_smaller.write(f"#define {sanitized_char}_height {smaller_height}\n")
            f_smaller.write(f"static char {sanitized_char}_bits[] = {{\n")
            for i, byte in enumerate(xbm_data):
                f_smaller.write(f"0x{byte:02X}")
                if i < len(xbm_data) - 1:
                    f_smaller.write(", ")
                if (i + 1) % 12 == 0:
                    f_smaller.write("\n")
            f_smaller.write("};\n\n")

    print(f"XBM files saved as {file_name_default} and {file_name_smaller}.")



def bitmap_to_xbm(bitmap, forced_width, forced_height, padding_top=0, padding_bottom=0):
    # Create binary array and apply threshold
    img = Image.fromarray(bitmap, dtype=np.uint8)
    resized_array = np.array(img.resize((forced_width, forced_height), Image.Resampling.LANCZOS))
    binary_array = (resized_array > threshold_value).astype(np.uint8)

    # Calculate padding
    padded_height = forced_height + padding_top + padding_bottom
    padded_width = forced_width
    padded_array = np.zeros((padded_height, padded_width), dtype=np.uint8)

    # Place the character bitmap in the padded array
    padded_array[padding_top:padding_top + forced_height, :] = binary_array

    # Convert to XBM format
    xbm_data = []
    for row in padded_array:
        row_data = 0
        for col, bit in enumerate(row):
            if bit:
                row_data |= (1 << (7 - (col % 8)))
            if (col % 8) == 7:
                xbm_data.append(row_data)
                row_data = 0
        if (padded_width % 8) != 0:  # Handle any remaining bits in the row
            xbm_data.append(row_data)

    return xbm_data, padded_width, padded_height
