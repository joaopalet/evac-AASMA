import pygame
from settings import *
from sprites import *



# Auxiliary Functions

def draw_grid():
    for x in range(0, WIDTH, TILESIZE):
        pygame.draw.line(SCREEN, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILESIZE):
        pygame.draw.line(SCREEN, BLACK, (0, y), (WIDTH, y))

def get_layout():
    f = open('maze.txt', 'r').read()
    p = []
    p = [item.split() for item in f.split('\n')[:-1]]
    return p

def createWalls():
    for i in range(int(GRIDWIDTH)):
        for j in range(int(GRIDHEIGHT)):
            if layout[i][j] == 'W':
                wall = Wall(i,j)
                all_sprites.add(wall)
                all_walls.add(wall)

def createFires():
    for i in range(int(GRIDWIDTH)):
        for j in range(int(GRIDHEIGHT)):
            if layout[i][j] == 'F':
                fire = Fire(i,j)
                all_sprites.add(fire)
                all_fires.add(fire)



# Main

if __name__ == "__main__":
    global SCREEN, CLOCK, layout, all_sprites, all_players, all_walls, all_fires

    pygame.init()
    pygame.display.set_caption("Evacuation Simulation")
    pygame.key.set_repeat(200, 100)
    SCREEN = pygame.display.set_mode((HEIGHT, WIDTH))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(BLACK)

    # Create agents
    layout = get_layout()
    all_sprites = pygame.sprite.Group()
    all_walls   = pygame.sprite.Group()
    all_players = pygame.sprite.Group()
    all_fires   = pygame.sprite.Group()
    createWalls()
    createFires()
    player = Player(1, 1, all_walls, layout, all_fires) #Player(pos, all_walls, layout)
    all_sprites.add(player)
    all_players.add(player)
    plan = player.bfs([player.x, player.y], [14, 19])
    print(plan)

    # Main cycle
    run = True
    i = 1
    while run:
        CLOCK.tick(FPS)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move(dx = -1)
                if event.key == pygame.K_RIGHT:
                    player.move(dx = +1)
                if event.key == pygame.K_UP:
                    player.move(dy = -1)
                if event.key == pygame.K_DOWN:
                    player.move(dy = +1)
        
        player.move(dx = (plan[i][0] - player.x), dy = (plan[i][1] - player.y))        

        # Update
        all_sprites.update()

        # Render
        SCREEN.fill(WHITE)
        all_sprites.draw(SCREEN)
        draw_grid()
        pygame.display.flip()

        i += 1

    pygame.quit()



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