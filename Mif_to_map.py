def print_characters_from_mif_16x32(mif_file, char_width=16, char_height=32):
    def hex_to_binary(hex_value, width):
        return bin(int(hex_value, 16))[2:].zfill(width)

    try:
        with open(mif_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{mif_file}' not found!")
        return

    # Filter relevant lines
    content_lines = [line.strip() for line in lines if ":" in line]
    print(f"Content Lines: {content_lines}")

    if not content_lines:
        print("No valid content lines found in the file.")
        return

    current_bitmap = []
    print("=== Parsed Characters ===")

    for line in content_lines:
        try:
            address, data = line.split(":")
            hex_values = data.strip().split(" ")
            binary_row = "".join(hex_to_binary(hex_value, 8) for hex_value in hex_values)
            print(f"Address: {address}, Data: {hex_values}, Binary Row: {binary_row}")
            current_bitmap.append(binary_row[:char_width])
        except ValueError as e:
            print(f"Error parsing line: {line}. Exception: {e}")
            continue

        if len(current_bitmap) == char_height:
            for row in current_bitmap:
                print("".join("#" if bit == "1" else "." for bit in row))
            print("\n--- End of Character ---\n")
            current_bitmap = []  # Reset for next character
