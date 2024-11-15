def bitmap_to_xbm(bitmap, forced_width, forced_height, threshold_value=40, padding_top=0, padding_bottom=0, padding_left=0, padding_right=0, use_smaller_padding=False, smaller_padding_bottom=0):
    # Convert the input bitmap to a numpy array
    bitmap_array = np.array(bitmap.buffer, dtype=np.uint8).reshape(bitmap.rows, bitmap.width)
    
    # Create an image from the array and resize it to the forced dimensions
    img = Image.fromarray(bitmap_array)
    img_resized = img.resize((forced_width, forced_height), Image.Resampling.LANCZOS)
    
    # Convert resized image to binary (black-and-white) array based on the threshold
    resized_array = np.array(img_resized)
    binary_array = (resized_array > threshold_value).astype(np.uint8)
    
    # Clean up the binary array if necessary (using a cleanup function for isolated pixels)
    cleaned_array = cleanup_image(binary_array)
    
    # Choose padding_bottom based on the use_smaller_padding flag
    effective_padding_bottom = smaller_padding_bottom if use_smaller_padding else padding_bottom
    
    # Apply padding by creating a new array with extra rows/columns for the specified padding
    padded_height = forced_height + padding_top + effective_padding_bottom
    padded_width = forced_width + padding_left + padding_right
    padded_array = np.zeros((padded_height, padded_width), dtype=np.uint8)
    
    # Place the cleaned character bitmap in the center of the padded array
    padded_array[padding_top:padding_top + forced_height, padding_left:padding_left + forced_width] = cleaned_array
    
    # Initialize the XBM data list and calculate the number of bytes per row
    xbm_data = []
    bytes_per_row = (padded_width + 7) // 8  # Calculate bytes per row based on width
    
    # Convert each row to byte values
    for row in padded_array:
        row_data = []
        byte_value = 0
        for col in range(padded_width):
            # Set bit if pixel is on (value > 0)
            if row[col] > 0:
                byte_value |= (1 << (7 - (col % 8)))
            
            # Append the byte to the row_data when full or end of the row is reached
            if (col % 8) == 7:
                row_data.append(byte_value)
                byte_value = 0
        
        # Append any remaining bits as a byte if the row width is not a multiple of 8
        if (padded_width % 8) != 0:
            row_data.append(byte_value)
        
        # Add the row data to XBM data
        xbm_data.extend(row_data)

    # Return the XBM data, along with the padded dimensions for compatibility with the original function
    return xbm_data, padded_width, padded_height
