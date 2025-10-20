def unittest(data_path, temp_path):
    import image
    img = image.Image("unittest/data/apriltags.pgm", copy_to_fb=True)
    tags = img.find_apriltags()
    if len(tags) != 1:
        return False
    tag = tags[0]
    # AprilTag objects use attribute access, not subscripting
    # Expected values: x=45, y=27, w=69, h=69, id=255, family=16, cx=79, cy=61
    return (tag.x == 45 and tag.y == 27 and tag.w == 69 and tag.h == 69 and
            tag.id == 255 and tag.family == 16 and tag.cx == 79 and tag.cy == 61)
