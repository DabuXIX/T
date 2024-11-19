def run_conversion(ttf_path, output_dir, char_list, forced_height_1, forced_height_2, max_width, padding_top, bottom_padding_1, bottom_padding_2):
    """Run the full conversion process, including XBM, MIF, and BIN generation."""
    try:
        # Generate XBM data
        all_xbm_data = generate_xbm_data(
            ttf_path, char_list, 
            forced_height_1=forced_height_1, 
            forced_height_2=forced_height_2, 
            max_width=max_width, 
            padding_top=padding_top, 
            bottom_padding_1=bottom_padding_1, 
            bottom_padding_2=bottom_padding_2
        )
        
        # Write combined XBM file
        write_xbm(all_xbm_data, os.path.join(output_dir, "combined.xbm"), char_list)
        
        # Write MIF files for both forced heights
        write_mif(char_list, all_xbm_data, output_dir, forced_height_1)
        write_mif(char_list, all_xbm_data, output_dir, forced_height_2)
        
        # Write combined binary file
        write_bin(char_list, all_xbm_data, output_dir)
        
        messagebox.showinfo("Success", "Conversion completed successfully! All files generated.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion: {e}")
