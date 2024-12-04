from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os


def reverse_bits(byte):
    """Reverse the bits in a single byte (8 bits)."""
    reversed_byte = 0
    for i in range(8):
        if byte & (1 << i):
            reversed_byte |= (1 << (7 - i))
    return reversed_byte


def generate_xbm_data(ttf_path, char_list, forced_height, max_width, canvas_width, canvas_height,
                      threshold_value=128, padding_top=0, padding_bottom=0):
    """
    Generates XBM data for characters, ensuring proper padding and alignment.
    Handles punctuation scaling (e.g., commas, periods) with bottom alignment.
    """
    font_size = forced_height * 2
    font = ImageFont.truetype(ttf_path, font_size)
    all_xbm_data = {}

    # Define punctuation characters and a scaling ratio
    punctuation_set = {',', '.'}
    punctuation_scale = 0.25  # Typically, punctuation is 40% of the height of regular characters

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

            # Center horizontally
            horizontal_padding = (canvas_width - scaled_width) // 2

            # Place character in padded array
            padded_array[vertical_start:vertical_start + target_height,
                         horizontal_padding:horizontal_padding + scaled_width] = binary_array

            # Convert each row to two bytes (16 bits)
            xbm_data = []
            for row in padded_array:
                byte1, byte2 = 0, 0
                for col in range(8):  # First byte (leftmost 8 bits)
                    if row[col]:
                        byte1 |= (1 << (7 - col))
                for col in range(8, 16):  # Second byte (rightmost 8 bits)
                    if col < canvas_width and row[col]:
                        byte2 |= (1 << (7 - (col - 8)))  # Adjust bit position correctly

                # Reverse bits for compatibility
                byte1 = reverse_bits(byte1)
                byte2 = reverse_bits(byte2)

                xbm_data.append((byte1, byte2))  # Append as a tuple of 2 bytes

            all_xbm_data[char] = xbm_data

        except Exception as e:
            print(f"Warning: Unable to process character '{char}'. Reason: {e}")

    return all_xbm_data




def write_xbm(all_xbm_data, output_file, canvas_width, canvas_height):
    """
    Writes XBM data to a file in the desired format, explicitly appending the space character at the end.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# XBM File\n\n")

        for char, xbm_data in all_xbm_data.items():
            f.write(f"/* Character: '{char}' */\n")
            f.write(f"#define {char}_width {canvas_width}\n")
            f.write(f"#define {char}_height {canvas_height}\n")
            f.write(f"static char {char}_bits[] = {{\n")

            for byte1, byte2 in xbm_data:
                f.write(f"  0x{byte1:02X}, 0x{byte2:02X},\n")

            f.write("};\n\n")

        # Explicitly append the space character at the end
        f.write("/* Character: ' ' (space) */\n")
        f.write(f"#define SPACE_width {canvas_width}\n")
        f.write(f"#define SPACE_height {canvas_height}\n")
        f.write("static char SPACE_bits[] = {\n")

        for _ in range(canvas_height):
            f.write("  0x00, 0x00,\n")  # Blank rows for space

        f.write("};\n\n")

    print(f"XBM file saved as {output_file}")



def write_mif(all_xbm_data, output_file, canvas_width, canvas_height):
    """
    Writes character data to a MIF file, including strikeout characters appended at address 0x0A00,
    and ensures the space character is included at the end of both sections.
    """
    def add_strikeout(xbm_data, canvas_height):
        """Adds a horizontal strikeout line in the middle of the character."""
        strikeout_data = []
        middle_row = canvas_height // 2  # Find the middle row for strikeout
        for i, (byte1, byte2) in enumerate(xbm_data):
            if i == middle_row:  # Add strikeout on the middle row
                byte1 |= 0xFF  # Set all bits in the first byte
                byte2 |= 0xFF  # Set all bits in the second byte
            strikeout_data.append((byte1, byte2))
        return strikeout_data

    with open(output_file, "w", encoding="utf-8") as f:
        # Write MIF header
        f.write("DEPTH = 4096;\n")
        f.write("WIDTH = 16;\n")
        f.write("ADDRESS_RADIX = HEX;\n")
        f.write("DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n\n")

        # Non-strikeout characters start at 0x0000
        address = 0x0000
        for char, xbm_data in all_xbm_data.items():
            f.write(f"-- Character: '{char}'\n")
            for byte1, byte2 in xbm_data:
                word = (byte1 << 8) | byte2  # Combine two bytes into a 16-bit word
                f.write(f"{address:04X} : {word:04X};\n")
                address += 1

        # Explicitly append the space character at the end of the non-strikeout section
        f.write("-- Character: ' ' (space)\n")
        for _ in range(canvas_height):
            f.write(f"{address:04X} : 0000;\n")
            address += 1

        # Strikeout characters start at 0x0A00
        address = 0x01000
        for char, xbm_data in all_xbm_data.items():
            f.write(f"-- Strikeout Character: '{char}'\n")
            strikeout_data = add_strikeout(xbm_data, canvas_height)
            for byte1, byte2 in strikeout_data:
                word = (byte1 << 8) | byte2  # Combine two bytes into a 16-bit word
                f.write(f"{address:04X} : {word:04X};\n")
                address += 1

        # Explicitly append the space character at the end of the strikeout section
        f.write("-- Strikeout Character: ' ' (space)\n")
        for _ in range(canvas_height):
            f.write(f"{address:04X} : 0000;\n")
            address += 1

        f.write("END;\n")
    print(f"MIF file saved as {output_file}")




def main():
    ttf_path = r"c:\WINDOWS\Fonts\CAMBRIA.TTC"  # Path to font
    char_list = (
        [chr(i) for i in range(0x20, 0x61)] +  
        [
            chr(0x7B), chr(0x7C), chr(0x7D), chr(0x7E), chr(0xB0), chr(0xB1),
            chr(0x2026),chr(0x2190), chr(0x2191), chr(0x2192), chr(0x2193),
            chr(0x21CC), chr(0x25BC), chr(0x2713), chr(0x20)
        ]
    )

    output_dir = r"C:\Users\theda\OneDrive\Desktop\out_test"  # Output directory

    # Configuration
    forced_height = 39
    max_width = 21
    canvas_width =32  # Canvas width in bits
    canvas_height = 64  # Canvas height in rows
    padding_top = 2
    padding_bottom = 23

    # Generate data
    os.makedirs(output_dir, exist_ok=True)
    xbm_data = generate_xbm_data(ttf_path, char_list, forced_height, max_width, canvas_width, canvas_height,
                                  padding_top=padding_top, padding_bottom=padding_bottom)

    # Write XBM and MIF files
    write_xbm(xbm_data, os.path.join(output_dir, "FontRom.xbm"), canvas_width, canvas_height)
    write_mif(xbm_data, os.path.join(output_dir, "FontRom.mif"), canvas_width, canvas_height)


if __name__ == "__main__":
    main()
