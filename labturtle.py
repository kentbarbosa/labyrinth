import math
import turtle as tu

size = width, height = 320, 320
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255


ringscale = 10.0
x_offset = 200
y_offset = 200

rings = []
for ring in range(2,11):
    if ring[rings] is None:
        ring[rings] = []
    lastpt = None
    for radial in range(8):
        angle = radial * math.pi/4
        x = ring * ringscale * math.cos(angle) + x_offset
        y = ring * ringscale * math.sin(angle) + y_offset
        if lastpt :
            rings[ring].append([lastpt,(x,y)])
        lastpt = (x,y)        
        print("{}, {}".format(x,y))

print(rings)

for ring in rings:
    for lines in ring:
        for line in lines:
            print("draw line {}, {}".format(line[0],line[1]))
            tu.pencolor("yellow")
            tu.penup()
            tu.goto(line[0)
            tu.pendown()
            tu.goto(line[1])
            tu.penup()


