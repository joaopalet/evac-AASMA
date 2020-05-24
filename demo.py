import pygame
from auxiliary import *
from random import choices
from settings import *
from sprites import *
from copy import deepcopy
import time

import matplotlib.pyplot as plt
import os


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
	
	#propagar com base nos fogos
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


def assertInRange(speaker, listener):
	return abs(speaker.x - listener.x)<=speaker.getVolume() and abs(speaker.y - listener.y)<=speaker.getVolume()

def communicate(speaker):
	if (not speaker.isCommunicative()):
		return
	for listener in all_agents:
		if (speaker.getID() == listener.getID()): continue
		if assertInRange(speaker, listener):
			listener.receiveMessage(speaker.getLayout())

#ARGUMENTS: there's communication , there's alarm, num_agents, percentage of risk_taking agents,  percentage of communicative agents, vision range
def mainCycle(lay, com, alar, num_ag, perc_R, perc_C, rang, vol):
	global SCREEN, CLOCK, layout, all_sprites, all_agents, all_walls, all_fires, all_smokes, all_alarms, exits, soundAlarm, run, pause, agents_dead, agents_saved, fire_alarm

	soundAlarm = False

	# Create agents
	layout = getLayout(lay)
	exits  = getExitsPos(layout)

	all_sprites = pygame.sprite.Group()
	all_walls   = pygame.sprite.Group()
	all_agents  = pygame.sprite.Group()
	all_fires   = pygame.sprite.Group()
	all_smokes  = pygame.sprite.Group()
	all_alarms  = pygame.sprite.Group()
	createWalls()
	createAlarm()

	num_riskT = int((perc_R/100)*num_ag)
	num_comm  = int((perc_C/100)*num_ag)
	c = 0
	for i in range(num_ag):
		if(i < num_riskT and i%2==0):
			if(c < num_comm):   
				#print('risk taking and communicative')
				player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 1, True)
				c += 1
			else: 
				#print('risk taking and non communicative')
				player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 1, False)
		elif(i < num_riskT and (i%2!=0 or num_comm == 0)):
			#print('risk taking and non communicative')  
			player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 1, False)
		elif(i >= num_riskT and i%2==0):
			if(c < num_comm):
				#print('not risk taking and communicative') 
				player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 0, True)
				c += 1
			else: 
				#print('not risk taking and not communicative')
				player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 0, False)
		elif(i >= num_riskT and (i%2!=0 or num_comm == 0)):
			#print('not risk taking and not communicative')
			player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 0, False)
		player.setRange(rang)
		player.setVolume(vol)
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
				
		if len(agents_saved) + len(agents_dead) == num_ag: #or maybe if(len(all_fires))==WIDTH*HEIGHT-walls-alarm-...
			break

		if not pause:
			for agent in all_agents:
				agent.percept(layout)
				agent.checkAlarm(soundAlarm)
				if(com): communicate(agent)
			for agent in all_agents:
				agent.plan_()
				updateHealth(agent)

			if (i%2 == 0): layout = propagateFire(layout)
			if (i%1 == 0): layout = propagateSmoke(layout)

			if(alar): alarm()

			all_agents.update(all_agents)

		i+=1
	
	print('agents saved: ', len(agents_saved))
	return len(agents_saved)/num_ag

# Main
if __name__ == "__main__":
    global SCREEN, CLOCK, layout, all_sprites, all_agents, all_walls, all_fires, all_smokes, exits, soundAlarm, run, pause

    if os.path.exists("res.txt"): os.remove("res.txt")
    
    f = open("res.txt", "a")

    numIt = 100       #numero iteracoes
    com   = True      #comunicacao
    alar  = True      #alarme
    rang  = RANGE     #vision range
    numAg = 50
    vol   = VOLUME    #volume range

    x_ = [None]*3
    y_ = [None]*3

    # BASELINE - 50 agentes, 50% risk taking, 50% communicative, RANGE = 5, VOLUME = 5, Mapa com 2 saidas
    print('BASELINE')
    res1 = 0
    for i in range(numIt):
        res1 += mainCycle(None, com, alar, numAg, 50, 50, rang, vol)
    final1 = (res1/numIt)*100
    f.write("BASELINE: %f\n\n" % final1)
    x_[1] = 2
    y_[1] = final1

    # MAPA COM 1 SAIDA
    print('MAPA 1 SAIDA')
    res = 0
    for i in range(numIt):
        res += mainCycle('supermarket1.txt', com, alar, numAg, 50, 50, rang, vol)
    final2 = (res/numIt)*100
    f.write("MAPA COM 1 SAIDA: %f\n\n" % final2)
    x_[0] = 1
    y_[0] = final2

    # MAPA COM 3 SAIDAS
    print('MAPA 3 SAIDA')
    res = 0
    for i in range(numIt):
        res += mainCycle('supermarket3.txt', com, alar, numAg, 50, 50, rang, vol)
    final3 = (res/numIt)*100
    f.write("MAPA COM 3 SAIDAS: %f\n\n" % final3)
    x_[2] = 3
    y_[2] = final3

    plt.figure()
    plt.ylabel("Saved Evacuees (%)")
    plt.xlabel("Number of Exits")
    plt.plot(x_,y_)
    plt.savefig('NºEXITS.png')


    # VARIAR Nº AGENTES
    x = []
    y = []
    for j in range(10, 110, 10):
        res2 = 0
        x.append(j)
        for i in range(numIt):
            res2 += mainCycle(None, com, alar, j, 50, 50, rang, vol)
        final2 = (res2/numIt)*100
        y.append(final2)
    
    plt.figure()
    plt.ylabel("Saved Evacuees (%)")
    plt.xlabel("Number of Evacuees")
    plt.plot(x,y)
    plt.savefig('NºAGENTES.png')

    
    # VARIAR % DE AGENTES RISK_TAKING
    x = []
    y = []
    for j in range(0, 110, 20):     # j -> % of risk_taking agents
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(None, com, alar, numAg, j, 50, rang, vol)
        final = (res/numIt)*100
        y.append(final)

    plt.figure()
    plt.ylabel("Saved Evacuees (%)")
    plt.xlabel("Risk taking Evacuees (%)")
    plt.plot(x,y)
    plt.savefig('%RISK_TAKING.png')


    # VARIAR % DE COMMUNICATIVE AGENTS
    x = []
    y = []
    for j in range(0, 110, 20):     # j -> % of communicative agents
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(None, com,alar, numAg, 50, j, rang, vol)
        final = (res/numIt)*100
        y.append(final)

    plt.figure()
    plt.ylabel("Saved Evacuees (%)")
    plt.xlabel("Communicative Evacuees (%)")
    plt.plot(x,y)
    plt.savefig('%COMMUNICATIVE.png')


    # VARIAR VISION RANGE [1-10]
    x = []
    y = []
    for j in range(1, 11):
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(None, com, alar, numAg, 50, 50, j, vol)
        final = (res/numIt)*100
        y.append(final)
    
    plt.figure()
    plt.ylabel("Saved Evacuees (%)")
    plt.xlabel("Evacuee Vision RANGE")
    plt.plot(x,y)
    plt.savefig('VISION_RANGE.png')


    # VARIAR VOLUME RANGE [1-10]
    x = []
    y = []
    for j in range(1, 11):
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(None, com, alar, numAg, 50, 50, rang, j)
        final = (res/numIt)*100
        y.append(final)
    
    plt.figure()
    plt.ylabel("Saved Evacuees (%)")
    plt.xlabel("Evacuee Volume RANGE")
    plt.plot(x,y)
    plt.savefig('VOLUME_RANGE.png')


    # SEM ALARME
    res = 0
    for i in range(numIt):
        res += mainCycle(None, com, not alar, numAg, 50, 50, rang, vol)
    final = (res/numIt)*100
    f.write("SEM ALARME: %f\n\n" % final)