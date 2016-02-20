import sensor, image, time
sensor.reset()
sensor.set_framesize(sensor.QVGA)
# All drawing functions use the same code to pass color.
# So we just need to test one function.
while(True):
    # Test Draw Line (GRAYSCALE)
    sensor.set_pixformat(sensor.GRAYSCALE)
    for i in range(10):
        img = sensor.snapshot()
    for i in range(img.width()):
        c = ((i * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], int(c))
    sensor.snapshot()
    time.sleep(1000)
    for i in range(img.width()):
        c = (((img.width() -  i) * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], color = int(c))
    sensor.snapshot()
    time.sleep(1000)
    # Test Draw Line (RGB565)
    sensor.set_pixformat(sensor.RGB565)
    for i in range(10):
        img = sensor.snapshot()
    for i in range(img.width()):
        c = ((i * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], [int(c), 0, 0])
    sensor.snapshot()
    time.sleep(1000)
    for i in range(img.width()):
        c = (((img.width() -  i) * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], color = [int(c), 0, 0])
    sensor.snapshot()
    time.sleep(1000)
    # Test Draw Line (RGB565)
    sensor.set_pixformat(sensor.RGB565)
    for i in range(10):
        img = sensor.snapshot()
    for i in range(img.width()):
        c = ((i * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], [0, int(c), 0])
    sensor.snapshot()
    time.sleep(1000)
    for i in range(img.width()):
        c = (((img.width() -  i) * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], color = [0, int(c), 0])
    sensor.snapshot()
    time.sleep(1000)
    # Test Draw Line (RGB565)
    sensor.set_pixformat(sensor.RGB565)
    for i in range(10):
        img = sensor.snapshot()
    for i in range(img.width()):
        c = ((i * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], [0, 0, int(c)])
    sensor.snapshot()
    time.sleep(1000)
    for i in range(img.width()):
        c = (((img.width() -  i) * 255) + (img.width()/2)) / img.width()
        img.draw_line([i, 0, i, img.height()-1], color = [0, 0, int(c)])
    sensor.snapshot()
    time.sleep(1000)
