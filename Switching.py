# Generate XBM data with specific or default padding as applicable
xbm_data = bitmap_to_xbm(
    char,
    bitmap,
    actual_width,
    base_height,
    threshold_value=threshold_value,
    padding_top=pad_top if ascii_code in special_dimensions else padding_top,
    padding_bottom=pad_bot if ascii_code in special_dimensions else padding_bottom,
    padding_left=pad_left if ascii_code in special_dimensions else padding_left,
    padding_right=pad_right if ascii_code in special_dimensions else padding_right
)
