def unittest(data_path, temp_path):
    import image
    thresholds = [(0, 100, 56, 95, 41, 74),  # generic_red_thresholds
                  (0, 100, -128, -22, -128, 99),  # generic_green_thresholds
                  (0, 100, -128, 98, -128, -16)]     # generic_blue_thresholds
    # Load image
    img = image.Image("unittest/data/blobs.ppm", copy_to_fb=True)

    blobs = img.find_blobs(thresholds, pixels_threshold=2000, area_threshold=200)

    if len(blobs) != 3:
        return False

    # Allow small variations in blob metrics due to platform differences
    # Format: [x, y, w, h, pixels, cx, cy]
    expected = [
        [122, 41, 98, 82, 6260, 168, 82],
        [44, 42, 78, 88, 5158, 80, 84],
        [210, 40, 72, 82, 3986, 248, 77]
    ]

    tolerance = {
        0: 2,  # x, y - position tolerance
        1: 2,
        2: 2,  # w, h - dimension tolerance
        3: 2,
        4: 100,  # pixels - allow up to 100 pixel difference (~1.5%)
        5: 2,  # cx, cy - centroid tolerance
        6: 2
    }

    for i, blob in enumerate(blobs):
        actual = [int(x) for x in blob[0:-5]]
        for j, (exp, act) in enumerate(zip(expected[i], actual)):
            if abs(exp - act) > tolerance[j]:
                return False

    return True
