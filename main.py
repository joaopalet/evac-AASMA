import pygame
from auxiliary import *
from random import choices
from settings import *
from sprites import *
from copy import deepcopy
import time


def drawGrid():
    for x in range(0, WIDTH, TILESIZE):
        pygame.draw.line(SCREEN, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILESIZE):
        pygame.draw.line(SCREEN, BLACK, (0, y), (WIDTH, y))

def updateHealth(agent):
	pos = agent.getPosition()
	identifier  = agent.getID()
	if (isExit(layout,pos[0], pos[1]) and identifier not in agents_saved):
		agents_saved.append(identifier)
		all_sprites.remove(agent)
		all_agents.remove(agent)

	if(agent.getHealth() > 0):
		if (isSmoke(layout,pos[0], pos[1])): 
			new_health = agent.getHealth() - SMOKE_DMG
			agent.setHealth(new_health)
		if (isFire(layout,pos[0], pos[1])): 
			new_health = agent.getHealth() - FIRE_DMG
			agent.setHealth(new_health)

	if(agent.getHealth() <= 0):
		agent.die()
		agent.setColor(BLACK)
		if (identifier not in agents_dead):
			agents_dead.append(identifier)

def createWalls():
    for i in range(int(GRIDWIDTH)):
        for j in range(int(GRIDHEIGHT)):
            if (isWall(layout,i,j)):
                wall = Wall(i,j)
                all_sprites.add(wall)
                all_walls.add(wall)


def createAlarm():
	pos = [ [index, row.index('A')] for index, row in enumerate(layout) if 'A' in row]
	for p in pos:
		i = p[0]
		j = p[1]
		alarm = Alarm(i,j)
		all_sprites.add(alarm)
		all_alarms.add(alarm)

def alarm():
	global soundAlarm
	for alarm in all_alarms:
		if(alarm.CheckAlarm(layout)):
			#pygame.mixer.Sound.play(fire_alarm)
			soundAlarm = True
			break
	if(soundAlarm):
		for alarm in all_alarms:
			alarm.FireAlarm()


def createFires():
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


def propagateFire(layout):
	spread    = [True, False] #either it spreads or not
	propagate = [FIRE,  1-FIRE]
	smoke     = [SMOKE, 1-SMOKE]
	row       = [-1, 0, 0, 1]
	col       = [0, -1, 1, 0]

	new_fires = []
	for fire in all_fires:
		i = random.randrange(0, 4)
		x = fire.x + row[i]
		y = fire.y + col[i]

		if (x > len(layout)-1 or y > len(layout[0])-1): continue

		propagate_ = propagate
		if (isSmoke(layout,x, y)):
			propagate_[0] += (1-propagate_[1])/2
			propagate_[1] = 1 - propagate_[0]
		if (choices(spread, propagate_)[0] and not isWall(layout,x,y) and not isFire(layout,x,y) and not isExit(layout,x,y)):
			for smoke in all_smokes:
				if smoke.x == x and smoke.y == y:
					all_smokes.remove(smoke)
					break
			new_fires.append([x,y])

	for fire in new_fires:
		addFire(fire[0], fire[1])

	return layout


def propagateSmoke(layout):
	spread = [True, False]        #either it spreads or not
	wind   = [0.4, 0.3, 0.2, 0.1]
	smk    = [SMOKE, 1-SMOKE]
	row    = [-1, 0, 0, 1]
	col    = [0, -1, 1, 0]
	
	for fire in all_fires:

		for i in range(len(row)):

			x = fire.x + row[i]
			y = fire.y + col[i]

			if (x > len(layout)-1 or y > len(layout[0])-1): continue

			if (choices(spread, smk)[0] and validPropagation(layout,x,y)):
				addSmoke(x,y)
			if (choices(spread, smk)[0] and validPropagation(layout,x,y)):
				addSmoke(x,y)
			if (choices(spread, smk)[0] and validPropagation(layout,x,y)):
				addSmoke(x,y)
			if (choices(spread, smk)[0] and validPropagation(layout,x,y)):
				addSmoke(x,y)


	for smoke in all_smokes:

		for i in range(len(row)):

			x = smoke.x + row[i]
			y = smoke.y + col[i]

			if (x > len(layout)-1 or y > len(layout[0])-1): continue

			go = choices(spread, smk)[0]
			if (go and validPropagation(layout,x,y)):
				addSmoke(x, y)
			if (go and validPropagation(layout,x,y)):
				addSmoke(x, y)
			if (go and validPropagation(layout,x,y)):
				addSmoke(x, y)
			if (go and validPropagation(layout,x,y)):
				addSmoke(x, y)

	return layout


def draw():				
	SCREEN.fill(WHITE)
	all_walls.draw(SCREEN)
	all_smokes.draw(SCREEN)
	all_fires.draw(SCREEN)
	all_alarms.draw(SCREEN)
	all_agents.draw(SCREEN)
	s = 'Saved Agents: ' + str(len(agents_saved))
	drawText(SCREEN, s, 34, WIDTH/3, HEIGHT)
	s = 'Dead Agents: ' + str(len(agents_dead))
	drawText(SCREEN, s, 34, 2*WIDTH/3, HEIGHT)
	drawGrid()
	pygame.display.flip()

# Draw Text in screen
font_name = pygame.font.match_font('arial')
def drawText(surf, text, size, x, y):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE, BLACK)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (int(x),int(y))
	surf.blit(text_surface, text_rect)

def assertInRange(speaker, listener):
	return abs(speaker.x - listener.x)<=VOL_RANGE and abs(speaker.y - listener.y)<=VOL_RANGE

def communicate(speaker):
	if (not speaker.isCommunicative()):
		return
	for listener in all_agents:
		if (speaker.getID() == listener.getID()): continue
		if assertInRange(speaker, listener):
			listener.receiveMessage(speaker.getLayout())


# Main
if __name__ == "__main__":
	global SCREEN, CLOCK, layout, all_sprites, all_agents, all_walls, all_fires, all_smokes, exits, soundAlarm

	soundAlarm = False

	pygame.init()
	pygame.display.set_caption("Evacuation Simulation")
	SCREEN = pygame.display.set_mode((WIDTH, HEIGHT+40))
	CLOCK = pygame.time.Clock()
	SCREEN.fill(BLACK)

	# Create agents
	layout = getLayout(None)
	exits  = getExitsPos(layout)

	all_sprites = pygame.sprite.Group()
	all_walls   = pygame.sprite.Group()
	all_agents  = pygame.sprite.Group()
	all_fires   = pygame.sprite.Group()
	all_smokes  = pygame.sprite.Group()
	all_alarms  = pygame.sprite.Group()
	createWalls()
	createAlarm()
	#fire_alarm = pygame.mixer.Sound("FireAlarm.wav")

	for i in range(NUM_AGENTS):
		player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 1, True)
		all_sprites.add(player)
		all_agents.add(player)

	createFires()
	
	pause = False
	run   = True
	
	agents_saved = []
	agents_dead = []

	# Main cycle
	i = 0
	while run:
		
		CLOCK.tick(FPS)
		
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					pause = not pause

		if pause:
			pygame.mixer.pause()
		else:
			pygame.mixer.unpause()


		if len(agents_saved) + len(agents_dead) == NUM_AGENTS:
			break

		if not pause:
			
			for agent in all_agents:
				agent.percept(layout)
				agent.checkAlarm(soundAlarm)
				communicate(agent)
			for agent in all_agents:
				agent.plan_()
				updateHealth(agent)

			if (i%2 == 0): layout = propagateFire(layout)
			if (i%1 == 0): layout = propagateSmoke(layout)

			alarm()

			all_agents.update(all_agents)
			draw()

		i+=1

	pygame.mixer.pause()
	time.sleep(2)
	pygame.quit()