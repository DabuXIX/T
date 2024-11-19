def parse_jam_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    print("JAM Operations Found:")
    for line in lines:
        if line.strip().startswith(("SHIFT_IR", "SHIFT_DR", "SET_STATE", "WAIT")):
            print(line.strip())

# Replace with your JAM file path
parse_jam_file("output.jam")
