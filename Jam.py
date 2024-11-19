def parse_jam_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    print("JAM Operations Found:")
    for line in lines:
        if line.strip().startswith(("SHIFT_IR", "SHIFT_DR", "SET_STATE", "WAIT")):
            print(line.strip())

# Replace with your JAM file path
parse_jam_file("output.jam")





def extract_opcodes(file_path):
    opcodes = set()
    
    with open(file_path, 'r') as file:
        for line in file:
            # Extract the first word of each line (potential opcode)
            words = line.strip().split()
            if words:  # Ignore empty lines
                opcode = words[0]
                # Filter out comments and non-opcode lines
                if not opcode.startswith(("//", "#")):
                    opcodes.add(opcode)
    
    print("Unique Opcodes Found in the JAM File:")
    for opcode in sorted(opcodes):
        print(opcode)

# Replace with the path to your JAM file
extract_opcodes("output.jam")
