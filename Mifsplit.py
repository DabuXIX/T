def split_mif_32x64_to_16x64(input_file, output_dir):
    """
    Splits a 32x64 MIF file into two separate 16x64 MIF files: one for the lower 16 bits (Low) and one for the upper 16 bits (High).
    """
    import os

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    low_output_file = os.path.join(output_dir, "FontRom16x64_Low.mif")
    high_output_file = os.path.join(output_dir, "FontRom16x64_High.mif")

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Initialize content lists for high and low files
    header = []
    low_content = []
    high_content = []

    # Read header and content
    in_content_section = False
    for line in lines:
        stripped = line.strip()

        if stripped.startswith("CONTENT BEGIN"):
            in_content_section = True
            low_content.append("CONTENT BEGIN\n")
            high_content.append("CONTENT BEGIN\n")
        elif stripped.startswith("END;"):
            in_content_section = False
            low_content.append("END;\n")
            high_content.append("END;\n")
        elif not in_content_section:
            header.append(line)
        elif in_content_section:
            # Skip comment lines
            if stripped.startswith("--"):
                low_content.append(line)
                high_content.append(line)
                continue

            if ":" in stripped:
                address, data = stripped.split(":")
                address = address.strip()
                data = data.strip().replace(";", "")

                # Split 32-bit data into two 16-bit parts
                if len(data) == 8:  # Ensure it's a 32-bit hex value
                    low_data = data[4:8]  # Lower 16 bits
                    high_data = data[0:4]  # Upper 16 bits

                    low_content.append(f"{address} : {low_data};\n")
                    high_content.append(f"{address} : {high_data};\n")

    # Write Low MIF file
    with open(low_output_file, "w", encoding="utf-8") as low_f:
        low_f.writelines(header)
        low_f.writelines(low_content)

    # Write High MIF file
    with open(high_output_file, "w", encoding="utf-8") as high_f:
        high_f.writelines(header)
        high_f.writelines(high_content)

    print(f"MIF file split into: \n  Low: {low_output_file}\n  High: {high_output_file}")

# Example usage:
# split_mif_32x64_to_16x64("FontRom32x64.mif", "output_directory")
