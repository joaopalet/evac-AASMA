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
	propagate = [ALFA,  1-ALFA]
	smoke     = [SMOKE, 1-SMOKE]
	row       = [-1, 0, 0, 1]
	col       = [0, -1, 1, 0]

	new_fires = []
	for fire in all_fires:
		i = random.randrange(0, 4)
		x = fire.x + row[i]
		y = fire.y + col[i]
		propagate_ = propagate
		if (isSmoke(layout,x, y)):
			propagate_[0] += (1-propagate_[1])/2
			propagate_[1] = 1 - propagate_[0]
		if (choices(spread, propagate_)[0] and not isWall(layout,x, y) and not isFire(layout,x, y) and not isExit(layout,x, y)):
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
		x = fire.x
		y = fire.y
		if (choices(spread, smk)[0] and not isWall(layout,x+row[0], y+col[0]) and not isFire(layout,x+row[0], y+col[0]) and not isSmoke(layout,x+row[0], y+col[0]) and not isExit(layout,x+row[0], y+col[0])):
			addSmoke(x,y)
		if (choices(spread, smk)[0] and not isWall(layout,x+row[1], y+col[1]) and not isFire(layout,x+row[1], y+col[1]) and not isSmoke(layout,x+row[1], y+col[1]) and not isExit(layout,x+row[1], y+col[1])):
			addSmoke(x,y)
		if (choices(spread, smk)[0] and not isWall(layout,x+row[2], y+col[2]) and not isFire(layout,x+row[2], y+col[2]) and not isSmoke(layout,x+row[2], y+col[2]) and not isExit(layout,x+row[2], y+col[2])):
			addSmoke(x,y)
		if (choices(spread, smk)[0] and not isWall(layout,x+row[3], y+col[3]) and not isFire(layout,x+row[3], y+col[3]) and not isSmoke(layout,x+row[3], y+col[3]) and not isExit(layout,x+row[3], y+col[3])):
			addSmoke(x,y)

	for smoke in all_smokes:
		x = smoke.x
		y = smoke.y
		go = choices(spread, smk)[0]
		if (go and not isWall(layout,x+row[0], y+col[0]) and not isFire(layout,x+row[0], y+col[0]) and not isSmoke(layout,x+row[0], y+col[0]) and not isExit(layout,x+row[0], y+col[0])):
			addSmoke(x+row[0], y+col[0])
		if (go and not isWall(layout,x+row[1], y+col[1]) and not isFire(layout,x+row[1], y+col[1]) and not isSmoke(layout,x+row[1], y+col[1]) and not isExit(layout,x+row[1], y+col[1])):
			addSmoke(x+row[1], y+col[1])
		if (go and not isWall(layout,x+row[2], y+col[2]) and not isFire(layout,x+row[2], y+col[2]) and not isSmoke(layout,x+row[2], y+col[2]) and not isExit(layout,x+row[2], y+col[2])):
			addSmoke(x+row[2], y+col[2])
		if (go and not isWall(layout,x+row[3], y+col[3]) and not isFire(layout,x+row[3], y+col[3]) and not isSmoke(layout,x+row[3], y+col[3]) and not isExit(layout,x+row[3], y+col[3])):
			addSmoke(x+row[3], y+col[3])

	return layout


def assertInRange(speaker, listener):
	return abs(speaker.x - listener.x)<=VOLUME and abs(speaker.y - listener.y)<=VOLUME

def communicate(speaker):
	if (not speaker.isCommunicative()):
		return
	for listener in all_agents:
		if (speaker.getID() == listener.getID()): continue
		if assertInRange(speaker, listener):
			listener.receiveMessage(speaker.getLayout())


def mainCycle(com, alar, num_ag, perc, rang):     #communicate, there's alarm, num_agents, percentage of risk_taking agents
	global SCREEN, CLOCK, layout, all_sprites, all_agents, all_walls, all_fires, all_smokes, all_alarms, exits, soundAlarm, run, pause, agents_dead, agents_saved, fire_alarm

	soundAlarm = False

	# Create agents
	layout = getLayout()
	exits  = getExitsPos(layout)

	all_sprites = pygame.sprite.Group()
	all_walls   = pygame.sprite.Group()
	all_agents  = pygame.sprite.Group()
	all_fires   = pygame.sprite.Group()
	all_smokes  = pygame.sprite.Group()
	all_alarms  = pygame.sprite.Group()
	createWalls()
	createAlarm()

	num_riskT = (perc/100)*num_ag
	for i in range(num_ag):
		if(i < num_riskT): 
			player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 1, True)
		else: 
			player = Agent(i+1, deepcopy(layout), exits, HEALTH_POINTS, 0, True)
		player.setRange(rang)
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

    numIt = 500       #numero iteracoes
    com   = True      #comunicacao
    alar  = True      #alarme
    rang  = RANGE
    numAg = 50

    # CONFIG 1 - COM COMUNICACAO TODOS OS AGENTES RISK TAKING
    print('CONFIG 1 - COM COMUNICACAO TODOS OS AGENTES RISK TAKING')
    res1 = 0
    for i in range(numIt):
        print('i: ', i)
        res1 += mainCycle(com, alar, numAg, 100, rang)
        print('res: ', res1)
    final1 = (res1/numIt)*100
    f.write("% saved agents CONFIG 1: %f\n\n" % final1)

    # CONFIG 2 - SEM COMUNICACAO TODOS OS AGENTES RISK TAKING
    print('CONFIG 2 - SEM COMUNICACAO TODOS OS AGENTES RISK TAKING')
    res2 = 0
    for i in range(numIt):
        print('i: ', i)
        res2 += mainCycle(not com, alar, numAg, 100, rang)
        print('res: ', res2)
    final2 = (res2/numIt)*100
    f.write("% saved agents CONFIG 2: %f\n\n" % final2)

    # CONFIG 3 - SEM COMUNICACAO TODOS OS AGENTES RISK AVERSE
    print('CONFIG 3 - SEM COMUNICACAO TODOS OS AGENTES RISK AVERSE')
    res3 = 0
    for i in range(numIt):
        print('i: ', i)
        res3 += mainCycle(not com, alar, numAg, 0, rang)
        print('res: ', res3)
    final3 = (res3/numIt)*100
    f.write("% saved agents CONFIG 3: %f\n\n" % final3)

    # CONFIG 4 - COM COMUNICACAO TODOS OS AGENTES RISK AVERSE
    print('CONFIG 4 - COM COMUNICACAO TODOS OS AGENTES RISK AVERSE')
    res4 = 0
    for i in range(numIt):
        print('i: ', i)
        res4 += mainCycle(com, alar, numAg, 0, rang)
        print('res: ', res4)
    final4 = (res4/numIt)*100
    f.write("% saved agents CONFIG 4: %f\n\n" % final4)

    f.close()

    # CONFIG 5 - VARIAR Nº AGENTES [10-100], COM COMUNICACAO E COM ALARME
    print('CONFIG 5 - VARIAR Nº AGENTES [10-100], COM COMUNICACAO E COM ALARME')
    x = []
    y = []
    for j in range(10, 110, 10):
        res5 = 0
        x.append(j)
        for i in range(numIt):
            res5 += mainCycle(com, alar, j, 100, rang)
        final = (res5/numIt)*100
        y.append(final)
    
    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("number of agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_5.png')

    # CONFIG 6 - VARIAR Nº AGENTES [10-100], COM COMUNICACAO E SEM ALARME
    print('CONFIG 6 - VARIAR Nº AGENTES [10-100], COM COMUNICACAO E SEM ALARME')
    x = []
    y = []
    for j in range(10, 110, 10):
        res5 = 0
        x.append(j)
        for i in range(numIt):
            res5 += mainCycle(com, not alar, j, 100, rang)
        final = (res5/numIt)*100
        y.append(final)
    
    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("number of agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_6.png')

    # CONFIG 7 - VARIAR Nº AGENTES [10-100], SEM COMUNICACAO E COM ALARME
    print('CONFIG 7 - VARIAR Nº AGENTES [10-100], SEM COMUNICACAO E COM ALARME')
    x = []
    y = []
    for j in range(10, 110, 10):
        res5 = 0
        x.append(j)
        for i in range(numIt):
            res5 += mainCycle(not com, alar, j, 100, rang)
        final = (res5/numIt)*100
        y.append(final)
    
    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("number of agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_7.png')

    # CONFIG 8 - VARIAR Nº AGENTES [10-100], SEM COMUNICACAO E SEM ALARME
    print('CONFIG 8 - VARIAR Nº AGENTES [10-100], SEM COMUNICACAO E SEM ALARME')
    x = []
    y = []
    for j in range(10, 110, 10):
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(not com, not alar, j, 100, rang)
        final = (res/numIt)*100
        y.append(final)
    
    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("number of agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_8.png')


    # CONFIG 9 - VARIAR VARIAR RANGE [1-10] COM COMUNICACAO
    print('CONFIG 9 - VARIAR VARIAR RANGE [1-10] COM COMUNICACAO')
    x = []
    y = []
    for j in range(1, 11):
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(com, not alar, numAg, 100, j)
        final = (res/numIt)*100
        y.append(final)
    
    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("agent RANGE")
    plt.plot(x,y)
    plt.savefig('CONFIG_9.png')

    # CONFIG 10 - VARIAR VARIAR RANGE [1-10] SEM COMUNICACAO
    print('CONFIG 10 - VARIAR VARIAR RANGE [1-10] SEM COMUNICACAO')
    x = []
    y = []
    for j in range(1, 11):
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(not com, not alar, numAg, 100, j)
        final = (res/numIt)*100
        y.append(final)
    
    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("agent RANGE")
    plt.plot(x,y)
    plt.savefig('CONFIG_10.png')


    # CONFIG 13 - VARIAR % DE AGENTES RISK_TAKING SEM COMUNICACAO E COM ALARME
    print('CONFIG 13 - VARIAR % DE AGENTES RISK_TAKING SEM COMUNICACAO E COM ALARME')
    x = []
    y = []
    for j in range(0, 110, 10):     # j -> % of risk_taking agents
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(not com, alar, numAg, j, rang)
        final = (res/numIt)*100
        y.append(final)

    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("% of risk taking agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_13.png')


    # CONFIG 14 - VARIAR % DE AGENTES RISK_TAKING COM COMUNICACAO E COM ALARME
    print('CONFIG 14 - VARIAR % DE AGENTES RISK_TAKING COM COMUNICACAO E COM ALARME')
    x = []
    y = []
    for j in range(0, 110, 10):     # j -> % of risk_taking agents
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(com, alar, numAg, j, rang)
        final = (res/numIt)*100
        y.append(final)

    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("% of risk taking agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_14.png')

    # CONFIG 15 - VARIAR % DE AGENTES RISK_TAKING SEM COMUNICACAO E SEM ALARME
    print('CONFIG 15 - VARIAR % DE AGENTES RISK_TAKING SEM COMUNICACAO E SEM ALARME')
    x = []
    y = []
    for j in range(0, 110, 10):     # j -> % of risk_taking agents
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(not com, not alar, numAg, j, rang)
        final = (res/numIt)*100
        y.append(final)

    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("% of risk taking agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_15.png')

    # CONFIG 16 - VARIAR % DE AGENTES RISK_TAKING COM COMUNICACAO E SEM ALARME
    print('CONFIG 16 - VARIAR % DE AGENTES RISK_TAKING COM COMUNICACAO E SEM ALARME')
    x = []
    y = []
    for j in range(0, 110, 10):     # j -> % of risk_taking agents
        res = 0
        x.append(j)
        for i in range(numIt):
            res += mainCycle(com, not alar, numAg, j, rang)
        final = (res/numIt)*100
        y.append(final)

    plt.figure()
    #plt.title()
    plt.ylabel("% saved agents")
    plt.xlabel("% of risk taking agents")
    plt.plot(x,y)
    plt.savefig('CONFIG_16.png')