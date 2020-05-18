import pygame

# CLASSE AGENTE

if __name__ == "__main__":
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

# f = open( 'maze.txt' , 'r').read()
# l = []
# l = [item.split() for item in f.split('\n')[:-1]]

# print(l)

# W W W W W W W W W W W W W W W W W W W W
# W O O O W O O O W O O O W O O O O O O W
# W O O O W O O O W O O O W O O O O O O W
# W O O O W O O O W O O O W O O O O O O W
# W O O O W O O O W O O O W O O O O O O W
# W W O W W W O W W W O W W O O W O O O W
# W O O O O O O O O O O O O O O W O O O W
# W O O O O O O O O O O O O O O W O O O W
# W O O O O O O O O O O O O O O W O O O E
# W O O O O W W O W W W W W O O W O O O W
# W O O O O W W O W W W W W O O W O O O W
# W O O O O O O O O O O O O O O W O O O W
# W O O O O O O O O O O O O O O W O O O W
# W O O O O O O O O O O O O O O W O O O W
# W W W O W W W O W W W O W O O W O O O W
# W O O O W O O O W O O O W O O O O O O W
# W O O O W O O O W O O O W O O O O O O W
# W O O O W O O O W O O O W O O O O O O W
# W O O O W O O O W O O O W O O O O O O W
# W W W W W W W W W W W W W W W W W W W W