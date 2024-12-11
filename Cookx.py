def write_xbm(all_xbm_data, output_file, canvas_width, canvas_height):
    """
    Writes XBM data to a file, including both normal and strikeout versions.
    """
    def add_strikeout(xbm_data, canvas_width, canvas_height):
        """
        Adds a strikeout with three lines across the middle of the character.
        Centered relative to the grid for both configurations.
        """
        strikeout_data = []
        grid_width = 17 if canvas_width == 32 and canvas_height == 64 else canvas_width
        grid_height = 39 if canvas_width == 32 and canvas_height == 64 else canvas_height

        middle_start = (grid_height // 2) - 1
        middle_end = middle_start + 3  # Draw 3 rows

        for i, row_bytes in enumerate(xbm_data):
            if middle_start <= i < middle_end:
                new_row = [0xFF] * len(row_bytes)
            else:
                new_row = row_bytes[:]
            strikeout_data.append(new_row)

        return strikeout_data

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# XBM File\n\n")

        normal_data = []
        strikeout_data = []

        for char, xbm_data in all_xbm_data.items():
            normal_data.append((char, xbm_data))
            strikeout_data.append((char, add_strikeout(xbm_data, canvas_width, canvas_height)))

        # Write normal characters
        for char, xbm_data in normal_data:
            f.write(f"/* Character: '{char}' */\n")
            f.write(f"#define {char}_width {canvas_width}\n")
            f.write(f"#define {char}_height {canvas_height}\n")
            f.write(f"static char {char}_bits[] = {{\n")

            for row_bytes in xbm_data:
                f.write("  " + ", ".join(f"0x{byte:02X}" for byte in row_bytes) + ",\n")

            f.write("};\n\n")

        # Write strikeout characters
        for char, strikeout in strikeout_data:
            f.write(f"/* Strikeout Character: '{char}' */\n")
            f.write(f"static char {char}_strikeout_bits[] = {{\n")

            for row_bytes in strikeout:
                f.write("  " + ", ".join(f"0x{byte:02X}" for byte in row_bytes) + ",\n")

            f.write("};\n\n")

    print(f"XBM file saved as {output_file}")
