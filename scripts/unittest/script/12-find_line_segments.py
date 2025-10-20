def unittest(data_path, temp_path):
    import image
    img = image.Image("unittest/data/shapes.ppm", copy_to_fb=True)
    lines = img.find_line_segments()

    # Hardware typically finds 7 segments, Unix port may find 8
    # Unix port detects additional rectangle edges due to higher sensitivity
    if len(lines) < 7:
        return False

    # Find the core segments that should be present across all platforms
    # These are the diagonal/angled line segments (not the rectangle edges)
    core_segments = [
        (104, 70, 114, 76),  # x1, y1, x2, y2
        (139, 51, 133, 41),
        (109, 37, 100, 46),
        (129, 73, 137, 64),
    ]

    # Check if all core segments are found (allowing small coordinate variation)
    found_segments = []
    for line in lines:
        x1, y1, x2, y2 = line[0:4]
        for seg in core_segments:
            if (abs(x1 - seg[0]) <= 1 and abs(y1 - seg[1]) <= 1 and
                abs(x2 - seg[2]) <= 1 and abs(y2 - seg[3]) <= 1):
                found_segments.append(seg)
                break

    return len(found_segments) >= 4
