def write_mif(all_xbm_data, output_file, canvas_width, canvas_height):
    """
    Writes MIF data to a file, including both normal and strikeout versions.
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
        # Write MIF header
        depth = 8192 if canvas_width == 16 and canvas_height == 32 else 16384
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {canvas_width};\n")
        f.write("ADDRESS_RADIX = HEX;\n")
        f.write("DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n\n")

        address = 0x0000
        normal_data = []
        strikeout_data = []

        for char, xbm_data in all_xbm_data.items():
            normal_data.append((char, xbm_data))
            strikeout_data.append((char, add_strikeout(xbm_data, canvas_width, canvas_height)))

        # Write normal characters
        for char, xbm_data in normal_data:
            f.write(f"-- Character: '{char}'\n")
            for row_bytes in xbm_data:
                word = "".join(f"{byte:02X}" for byte in row_bytes)
                f.write(f"{address:04X} : {word};\n")
                address += 1

        # Write strikeout characters
        for char, strikeout in strikeout_data:
            f.write(f"-- Strikeout Character: '{char}'\n")
            for row_bytes in strikeout:
                word = "".join(f"{byte:02X}" for byte in row_bytes)
                f.write(f"{address:04X} : {word};\n")
                address += 1

        f.write("END;\n")

    print(f"MIF file saved as {output_file}")
