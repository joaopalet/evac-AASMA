import pygame
from random import choices
from settings import *
from sprites import *


# Predicates

def isFire(i, j):
	return layout[i][j] == 'F'

def isSmoke(i, j):
	return layout[i][j] == 'S'

def isWall(i, j):
	return layout[i][j] == 'W'


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
	while(isWall(layout,x,y)):
		x = random.randrange(0, len(layout))
		y = random.randrange(0, len(layout[0]))
	addFire(x,y)
	x = random.randrange(0, len(layout))
	y = random.randrange(0, len(layout[0]))
	while(isWall(layout,x,y)):
		x = random.randrange(0, len(layout))
		y = random.randrange(0, len(layout[0]))
	addFire(x,y)

def addFire(i,j):
	fire = Fire(i,j)
	layout[i][j] = 'F'
	all_sprites.add(fire)
	all_fires.add(fire)

def addSmoke(i,j):
	smoke = Smoke(i,j)
	layout[i][j] = 'S'
	all_sprites.add(smoke)
	all_smokes.add(smoke)

"""
Propaga o fogo e o fumo.
Cada célula em fogo propaga-se para uma célula adjacente aleatória com probabilidade ALFA (ver settings.py)
Cada célula em fogo faz fumo numa célula adjacente aleatória com probabilidade SMOKE (ver settings.py)
"""
def propagateFire(layout):
	spread    = [True, False] #either it spreads or not
	wind 	  = [0.4, 0.3, 0.2, 0.1] #Norte Sul Este Oeste
	propagate = [ALFA,  1-ALFA]
	put_out   = [BETA,  1-BETA]
	smoke     = [SMOKE, 1-SMOKE]
	row = [-1, 0, 0, 1]
	col = [0, -1, 1, 0]

	#REMOVER FOGO:
	#for fire in all_fires:
	#	if (choices(spread, put_out)[0]):
	#		layout[fire.x][fire.y] = 'O'
	#		all_fires.remove(fire)
	#		all_sprites.remove(fire)

	new_fires = []
	for fire in all_fires:
		i = random.randrange(0, 4)
		x = fire.x + row[i]
		y = fire.y + col[i]
		propagate_ = propagate
		if (isSmoke(layout, x, y)): #aumenta a probabilidade de propagar o fogo para a casa (x,y)
			propagate_[0] += (1-propagate_[1])/2
			propagate_[1] = 1 - propagate_[0]
		if (choices(spread, propagate_)[0] and not isWall(x, y) and not isFire(x, y)):
			#if (isSmoke(layout,x,y)):
			#	all_smokes.remove()
			new_fires.append([x,y])

	for fire in new_fires:
		addFire(fire[0], fire[1])

	return layout

def propagateSmoke(layout):
	spread = [True, False] #either it spreads or not
	smoke  = [SMOKE, 1-SMOKE]
	row = [-1, 0, 0, 1]
	col = [0, -1, 1, 0]
	
	#propagar com base nos fogos
	for fire in all_fires:
		i = random.randrange(0, 4)
		x = fire.x + row[i]
		y = fire.y + col[i]
		if (choices(spread, smoke)[0] and not isWall(x, y) and not isFire(x, y) and not isSmoke(x, y)):
			addSmoke(x, y)

	for smoke in all_smokes:
		i = random.randrange(0, 4)
		x = smoke.x + row[i]
		y = smoke.y + col[i]
		if (choices(spread, smoke)[0] and not isWall(x, y) and not isFire(x, y) and not isSmoke(x, y)):
			addSmoke(x, y)
		#addSmoke(x+row[0], y+col[0])
		#addSmoke(x+row[1], y+col[1])
		#addSmoke(x+row[2], y+col[2])
		#addSmoke(x+row[3], y+col[3])


# Main

if __name__ == "__main__":
	global SCREEN, CLOCK, layout, all_sprites, all_agents, all_walls, all_fires, all_smokes

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
	all_smokes  = pygame.sprite.Group()
	createWalls()

	for i in range(NUM_AGENTS):
		player = Agent(i+1, (1,1), HEALTH_POINTS, layout, 1)
		all_sprites.add(player)
		all_agents.add(player)

	createFires()
	
	pause = True
	run   = True
	
	i=1
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
				agent.percept(layout)
				agent.plan_()
			
			
			if (i%2==0):
				layout = propagateFire(layout)
			layout = propagateSmoke(layout)

			all_sprites.update()
			SCREEN.fill(WHITE)
			all_walls.draw(SCREEN)
			all_smokes.draw(SCREEN)
			all_fires.draw(SCREEN)
			all_agents.draw(SCREEN)
			draw_grid()
			pygame.display.flip()
		i+=1

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