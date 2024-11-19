from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def strikeout_data(data, width):
    """ Adds a strikeout line across the 7th and 8th row of character data. """
    if len(data) >= 8:
        data[6] = 0xFF  # Add strikeout in the 7th row
        data[7] = 0xFF  # Add strikeout in the 8th row
    return data


def generate_xbm_data(ttf_path, char_list, forced_height_1, forced_height_2, max_width=7, threshold_value=70,
                      padding_top=1, bottom_padding_1=1, bottom_padding_2=2, padding_side="center"):
    """
    Generates XBM data for a list of characters with dual heights and strikeout options.
    Allows certain characters (e.g., periods, commas) to render at their natural dimensions.
    """
    font_size = max(forced_height_1, forced_height_2) * 2
    font = ImageFont.truetype(ttf_path, font_size)
    all_xbm_data = {}
    missing_characters = []  # Track missing characters
    period_set = {'.', ','}  # Characters to render at their natural height

    # Define configurations to process each height and variant
    output_configurations = [
        (forced_height_1, padding_top, bottom_padding_1, "normal"),
        (forced_height_1, padding_top, bottom_padding_1, "strikeout"),
        (forced_height_2, padding_top, bottom_padding_2, "normal"),
        (forced_height_2, padding_top, bottom_padding_2, "strikeout"),
    ]

    for height, top_padding, bottom_padding, variant_label in output_configurations:
        for char in char_list:
            try:
                # Determine if character should use forced height or native rendering
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
                    # Skip resizing for native rendering
                    img_resized = image
                else:
                    # Calculate aspect ratio and resize to forced height
                    aspect_ratio = image.width / image.height
                    new_width = min(int(height * aspect_ratio), max_width)
                    img_resized = image.resize((new_width, height), Image.Resampling.LANCZOS)

                resized_array = np.array(img_resized)
                binary_array = (resized_array > threshold_value).astype(np.uint8)

                # Apply padding to create an 8x16 array
                total_height = height + top_padding + bottom_padding
                padded_array = np.zeros((16, 8), dtype=np.uint8)

                # Calculate padding column alignment
                if padding_side == "right":
                    start_col = 0
                elif padding_side == "left":
                    start_col = 8 - new_width
                else:  # Default: center alignment
                    start_col = (8 - new_width) // 2

                # Place the character data in the padded array
                start_row = top_padding
                if use_native_height:
                    # Place the character data at the bottom of the padded array
                    bottom_row = padded_array.shape[0] - actual_height
                    padded_array[bottom_row:, start_col:start_col + width] = binary_array[:, :width]
                else:
                    # Place the character data as usual with top padding
                    padded_array[start_row:start_row + height, start_col:start_col + new_width] = binary_array[:, :new_width]

                # Apply strikeout if the variant is "strikeout"
                if variant_label == "strikeout" and not use_native_height:
                    padded_array = strikeout_data(padded_array.copy(), new_width)

                # Convert padded array to xbm_data (byte values)
                xbm_data = []
                for row in padded_array:
                    byte_value = 0
                    for col in range(8):
                        if row[col] > 0:
                            byte_value |= (1 << (7 - col))
                    xbm_data.append(byte_value)

                # Store the data in all_xbm_data
                if char not in all_xbm_data:
                    all_xbm_data[char] = {}
                all_xbm_data[char][f"{variant_label}_{height}"] = xbm_data

                print(f"Generated data for character '{char}', Height: {height if not use_native_height else 'native'}, Variant: {variant_label}, Data Length: {len(xbm_data)}")

            except Exception as e:
                # Log missing characters
                if char not in missing_characters:
                    missing_characters.append(char)
                print(f"Warning: Unable to process character '{char}'. Reason: {e}")

    # Log all missing characters at the end
    if missing_characters:
        print("\nThe following characters were not in the ttf file:")
        for char in missing_characters:
            print(f"- '{char}' (Unicode: {ord(char)})")

    return all_xbm_data



def write_xbm(all_xbm_data, output_file, char_list):
    """ Writes all character data to a combined XBM file in the specified order. """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Combined XBM file with dual heights and strikeout versions, grouped by type\n\n")

        # Write characters in the order: 13 Normal, 13 Strikeout, 14 Normal, 14 Strikeout
        for label in ["normal_13", "strikeout_13", "normal_14", "strikeout_14"]:
            for char in char_list:
                if label in all_xbm_data[char]:
                    xbm_data = all_xbm_data[char][label]
                    height = 13 if "13" in label else 14

                    f.write(f"/* Character: '{char}', Height: {height}, Variant: {label.split('_')[0]} */\n")
                    f.write(f"#define {char}_width 8\n")
                    f.write(f"#define {char}_height {len(xbm_data)}\n")
                    f.write(f"static char {char}_{label}_bits[] = {{\n")

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


def write_mif(char_list, all_xbm_data, output_dir, height, depth=4096, width=8):
    """
    Writes the data for each character to a separate MIF file for the specified height.
    Includes both normal and strikeout characters in the same file.
    """
    file_name = os.path.join(output_dir, f"FontRom_{height}.mif")
    with open(file_name, "w", encoding="utf-8") as f:
        # MIF header
        f.write(f"DEPTH = {depth};\n")
        f.write(f"WIDTH = {width};\n")
        f.write(f"ADDRESS_RADIX = HEX;\n")
        f.write(f"DATA_RADIX = HEX;\n")
        f.write("CONTENT BEGIN\n\n")

        current_address = 0x000
        strikeout_start = 0x0800

        # Write normal character data with comments
        f.write(f"-- Normal characters for height {height}\n")
        for char in char_list:
            label = f"normal_{height}"
            if label in all_xbm_data[char]:
                xbm_data = all_xbm_data[char][label]

                # Add a comment for the character
                f.write(f"-- Character: '{char}'\n")
                for i, byte in enumerate(xbm_data):
                    f.write(f"{current_address + i:04X} : {byte:02X};\n")
                f.write("\n")
                current_address += 16  # Increment address by 16 bytes per character

        # Write strikeout character data with comments
        f.write(f"\n-- Strikeout characters for height {height}\n")
        for char in char_list:
            label = f"strikeout_{height}"
            if label in all_xbm_data[char]:
                xbm_data = all_xbm_data[char][label]

                # Add a comment for the character
                f.write(f"-- Character: '{char}'\n")
                for i, byte in enumerate(xbm_data):
                    f.write(f"{strikeout_start + i:04X} : {byte:02X};\n")
                strikeout_start += 16  # Increment address by 16 bytes per character

        # MIF footer
        f.write("\nEND;\n")
    print(f"MIF file saved as {file_name}")


def write_bin(char_list, all_xbm_data, output_dir):
    """
    Creates a binary file combining all character data:
    - 13px height: Normal and Strikeout (0x0000 - 0x0FFF)
    - 14px height: Normal and Strikeout (0x1000 - 0x1FFF)
    - The last 2 bytes (0x1FFE, 0x1FFF) store a checksum.
    """
    binary_file_path = os.path.join(output_dir, "FontRom_combined.bin")
    data_array = [0x00] * 8192  # Initialize array for 8KB binary file

    # Define sections for binary file
    sections = {
        "normal_13": 0x0000,
        "strikeout_13": 0x0800,
        "normal_14": 0x1000,
        "strikeout_14": 0x1800,
    }

    # Populate the binary array
    for label, start_address in sections.items():
        current_address = start_address
        for char in char_list:
            if label in all_xbm_data[char]:
                xbm_data = all_xbm_data[char][label]

                # Write character data
                for i, byte in enumerate(xbm_data):
                    data_array[current_address + i] = byte
                current_address += 16  # Increment by 16 bytes per character

    # Compute checksum over the first 8190 bytes
    checksum = sum(data_array[:-2]) & 0xFFFF
    data_array[-2] = (checksum >> 8) & 0xFF  # High byte
    data_array[-1] = checksum & 0xFF         # Low byte

    # Write binary file
    with open(binary_file_path, "wb") as bin_file:
        bin_file.write(bytearray(data_array))

    print(f"Binary file saved as {binary_file_path}")



import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Your existing functions go here: generate_xbm_data, write_xbm, write_mif, write_bin, etc.

def run_conversion(ttf_path, output_dir, char_list, forced_height_1, forced_height_2, max_width, padding_top, bottom_padding_1, bottom_padding_2):
    """Run the conversion process."""
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
        write_xbm(all_xbm_data, os.path.join(output_dir, "combined.xbm"), char_list)
        write_mif(char_list, all_xbm_data, output_dir, forced_height_1)
        write_mif(char_list, all_xbm_data, output_dir, forced_height_2)
        write_bin(char_list, all_xbm_data, output_dir)
        messagebox.showinfo("Success", "Conversion completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_file(entry):
    """Open a file dialog and set the entry text to the selected file path."""
    file_path = filedialog.askopenfilename(filetypes=[("TrueType Font", "*.ttf")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def browse_directory(entry):
    """Open a directory dialog and set the entry text to the selected directory."""
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

# Build the GUI
def main_gui():
    root = tk.Tk()
    root.title("TTF to XBM Converter")
    
    # Define character list
    char_list = [chr(i) for i in range(0x20, 0x7F)]
    
    # TTF Path Input
    tk.Label(root, text="TTF File Path:").grid(row=0, column=0, sticky=tk.W)
    ttf_path_entry = tk.Entry(root, width=50)
    ttf_path_entry.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_file(ttf_path_entry)).grid(row=0, column=2)
    
    # Output Directory Input
    tk.Label(root, text="Output Directory:").grid(row=1, column=0, sticky=tk.W)
    output_dir_entry = tk.Entry(root, width=50)
    output_dir_entry.grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_directory(output_dir_entry)).grid(row=1, column=2)
    
    # Forced Height 1
    tk.Label(root, text="Forced Height 1:").grid(row=2, column=0, sticky=tk.W)
    height1_entry = tk.Entry(root, width=10)
    height1_entry.insert(0, "14")
    height1_entry.grid(row=2, column=1, sticky=tk.W)
    
    # Forced Height 2
    tk.Label(root, text="Forced Height 2:").grid(row=3, column=0, sticky=tk.W)
    height2_entry = tk.Entry(root, width=10)
    height2_entry.insert(0, "13")
    height2_entry.grid(row=3, column=1, sticky=tk.W)
    
    # Max Width
    tk.Label(root, text="Max Width:").grid(row=4, column=0, sticky=tk.W)
    max_width_entry = tk.Entry(root, width=10)
    max_width_entry.insert(0, "7")
    max_width_entry.grid(row=4, column=1, sticky=tk.W)
    
    # Padding Top
    tk.Label(root, text="Padding Top:").grid(row=5, column=0, sticky=tk.W)
    padding_top_entry = tk.Entry(root, width=10)
    padding_top_entry.insert(0, "1")
    padding_top_entry.grid(row=5, column=1, sticky=tk.W)
    
    # Bottom Padding 1
    tk.Label(root, text="Bottom Padding 1:").grid(row=6, column=0, sticky=tk.W)
    bottom_padding1_entry = tk.Entry(root, width=10)
    bottom_padding1_entry.insert(0, "1")
    bottom_padding1_entry.grid(row=6, column=1, sticky=tk.W)
    
    # Bottom Padding 2
    tk.Label(root, text="Bottom Padding 2:").grid(row=7, column=0, sticky=tk.W)
    bottom_padding2_entry = tk.Entry(root, width=10)
    bottom_padding2_entry.insert(0, "2")
    bottom_padding2_entry.grid(row=7, column=1, sticky=tk.W)
    
    # Convert Button
    def on_convert():
        ttf_path = ttf_path_entry.get()
        output_dir = output_dir_entry.get()
        try:
            forced_height_1 = int(height1_entry.get())
            forced_height_2 = int(height2_entry.get())
            max_width = int(max_width_entry.get())
            padding_top = int(padding_top_entry.get())
            bottom_padding_1 = int(bottom_padding1_entry.get())
            bottom_padding_2 = int(bottom_padding2_entry.get())
            
            run_conversion(
                ttf_path, output_dir, char_list, 
                forced_height_1, forced_height_2, 
                max_width, padding_top, bottom_padding_1, bottom_padding_2
            )
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid input: {ve}")
    
    tk.Button(root, text="Convert", command=on_convert).grid(row=8, column=1, pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main_gui()


# # Example usage
# ttf_path = r"c:\WINDOWS\Fonts\TIMES.TTF"
# char_list = [chr(i) for i in range(0x20, 0x7F)]  # Standard ASCII
# char_list += [chr(0xE9)]  # é (Latin Small Letter E with Acute)
# char_list += [chr(0x1F4A1)]  # 💡 (Light Bulb)
# char_list += [chr(0x2191), chr(0x2193), chr(0x2190), chr(0x2192), chr(0x2B07)]  # Arrows
# char_list += [chr(0x00B1)]  # ± (Plus-Minus Sign)
# char_list += [chr(0x2A0D)]  # ⨍ (Integral Average)

# output_dir = r"C:\Users\theda\Downloads\outtest"

# all_xbm_data = generate_xbm_data(
#     ttf_path, char_list, 
#     forced_height_1=14, 
#     forced_height_2=13, 
#     max_width=7, 
#     padding_top=1, 
#     bottom_padding_1=1, 
#     bottom_padding_2=2
# )

# write_xbm(all_xbm_data, os.path.join(output_dir, "combined.xbm"), char_list)
# write_mif(char_list, all_xbm_data, output_dir, 13)
# write_mif(char_list, all_xbm_data, output_dir, 14)
# write_bin(char_list, all_xbm_data, output_dir)
