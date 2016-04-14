import math
import sys, pygame
pygame.init()

size = width, height = 320, 320
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)

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

if 1:         
##while 1:
##    for event in pygame.event.get():
##        if event.type == pygame.QUIT: sys.exit()
##
    screen.fill(black)
    for ring in rings:
        for lines in ring:
            for line in lines:
                print("draw line {}, {}".format(line[0],line[1]))
                #pygame.draw.line(screen,white,int(line[0]),int(line[1]),2)

    pygame.display.flip()

