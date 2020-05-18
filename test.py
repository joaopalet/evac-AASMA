import pygame
pygame.init()

win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Evacuation Simulation")

run = True
x = 0
y = 0
while run:
    pygame.time.delay(50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # update display
    win.fill((0,0,0))
    pygame.draw.rect(win, (255,0,0), (x, y, 20, 20))
    pygame.display.update()

    x += 2

pygame.quit()