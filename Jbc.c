#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Function to read the JBC file into memory
uint8_t *read_jbc_file(const char *filename, size_t *file_size) {
    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("Failed to open JBC file");
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    *file_size = ftell(file);
    rewind(file);

    uint8_t *buffer = (uint8_t *)malloc(*file_size);
    if (!buffer) {
        perror("Failed to allocate memory for JBC file");
        fclose(file);
        return NULL;
    }

    fread(buffer, 1, *file_size, file);
    fclose(file);
    return buffer;
}

// Helper function to interpret an opcode
void interpret_opcode(uint8_t opcode, uint8_t *data, size_t data_size) {
    switch (opcode) {
        case 0x10:  // Example: SHIFT_IR
            printf("Executing SHIFT_IR: ");
            for (size_t i = 0; i < data_size; i++) {
                printf("%02X ", data[i]);
            }
            printf("\n");
            break;

        case 0x20:  // Example: SHIFT_DR
            printf("Executing SHIFT_DR: ");
            for (size_t i = 0; i < data_size; i++) {
                printf("%02X ", data[i]);
            }
            printf("\n");
            break;

        case 0x30:  // Example: RUNTEST
            printf("Executing RUNTEST: Delay for %u cycles\n", (unsigned int)data[0]);
            break;

        default:
            printf("Unknown opcode: 0x%02X\n", opcode);
            break;
    }
}

// Function to parse and execute the JBC file
void parse_jbc(uint8_t *buffer, size_t file_size) {
    size_t offset = 0;

    while (offset < file_size) {
        uint8_t opcode = buffer[offset++];
        uint8_t data_length = buffer[offset++];  // Next byte indicates the data length
        uint8_t *data = NULL;

        if (data_length > 0) {
            data = &buffer[offset];
            offset += data_length;
        }

        printf("Opcode: 0x%02X, Data Length: %u\n", opcode, data_length);
        interpret_opcode(opcode, data, data_length);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <JBC file>\n", argv[0]);
        return 1;
    }

    const char *jbc_filename = argv[1];
    size_t file_size = 0;

    // Read the JBC file
    uint8_t *jbc_data = read_jbc_file(jbc_filename, &file_size);
    if (!jbc_data) {
        return 1;
    }

    printf("Parsing JBC file: %s\n", jbc_filename);
    parse_jbc(jbc_data, file_size);

    // Cleanup
    free(jbc_data);
    return 0;
}
