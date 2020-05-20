import pygame
from random import choices
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
	x = random.randrange(0, len(layout))
	y = random.randrange(0, len(layout[0]))
	while(layout[x][y] == 'W'):
		x = random.randrange(0, len(layout))
		y = random.randrange(0, len(layout[0]))
	addFire(x,y)
	x = random.randrange(0, len(layout))
	y = random.randrange(0, len(layout[0]))
	while(layout[x][y] == 'W'):
		x = random.randrange(0, len(layout))
		y = random.randrange(0, len(layout[0]))
	addFire(x,y)

def addFire(i,j):
	fire = Fire(i,j)
	layout[i][j] = 'F'
	all_sprites.add(fire)
	all_fires.add(fire)

def propagateFire(layout):
	spread    = [True, False] #either it spreads or not
	propagate = [ALFA, 1-ALFA]
	put_out   = [BETA, 1-BETA]
	row = [-1, 0, 0, 1]
	col = [0, -1, 1, 0]
	for fire in all_fires:
		if (choices(spread, put_out)[0]):
			layout[fire.x][fire.y] = 'O'
			all_fires.remove(fire)
			all_sprites.remove(fire)

	new_fires = []
	for fire in all_fires:
		i = random.randrange(0, 4)
		x = fire.x + row[i]
		y = fire.y + col[i]
		if (layout[x][y] != 'W' and choices(spread, propagate)[0] and layout[x][y] != 'F'):
			new_fires.append([x,y])
	for fire in new_fires:
		addFire(fire[0], fire[1])

	return layout


# Main

if __name__ == "__main__":
	global SCREEN, CLOCK, layout, all_sprites, all_agents, all_walls, all_fires, ALFA

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
	all_agents  = pygame.sprite.Group()
	all_fires   = pygame.sprite.Group()
	createWalls()

	for i in range(NUM_AGENTS):
		player = Agent(i+1, (1,1), HEALTH_POINTS, layout, 1)
		all_sprites.add(player)
		all_agents.add(player)

	createFires()
	
	pause = True
	run   = True	
	
	# Main cycle
	while run:
		CLOCK.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					pause = not pause

		if pause:
			for agent in all_agents:
				agent.percept(layout) #hack
				agent.plan_()
			
			layout = propagateFire(layout)
			all_sprites.update()
			SCREEN.fill(WHITE)
			all_walls.draw(SCREEN)
			all_fires.draw(SCREEN)
			all_agents.draw(SCREEN)
			draw_grid()
			pygame.display.flip()

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