from PIL import Image
im = Image.open('map.png')
pixels = im.load()
x, y = im.size
# (255, 255, 255) пустота
# (0, 0, 0)       стена
# (255, 0, 0)     красный флаг
# (0, 0, 255)     синий флаг
# (150, 150, 150) железный блок
with open('map.txt', 'w') as f:
    for i in range(x):
        line = []
        for j in range(y):
            r, g, b = pixels[i, j]
            if (r, g, b) == (255, 255, 255):
                line.append('0')
            elif (r, g, b) == (0, 0, 0):
                line.append('1')
            elif (r, g, b) == (255, 0, 0):
                line.append('31')
            elif (r, g, b) == (0, 0, 255):
                line.append('32')
            elif (r, g, b) == (150, 150, 150):
                line.append('2')
        print(' '.join(line[:]), file=f)
print('Готово')
