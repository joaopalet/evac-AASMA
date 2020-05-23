# Sprites

import pygame
import random
from random import choices
import numpy as np
from settings import *
from auxiliary import *
import heapq
import math


class Agent(pygame.sprite.Sprite):
    def __init__(self, identifier, health, layout, risk, exits):
        pygame.sprite.Sprite.__init__(self)
        self.image  = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(DARKRED)
        self.rect = self.image.get_rect()


        self.id         = identifier
        self.health     = health
        self.risk       = risk
        self.layout     = layout
        self.plan       = []
        self.exits      = exits
        self.danger     = False
        self.reconsider = False
        self.dead       = False

        self.x = random.randrange(0, len(self.layout))
        self.y = random.randrange(0, len(self.layout[0]))

        while(isWall(self.layout,self.x,self.y) or isAlarm(self.layout, self.x,self.y) or isExit(layout, self.x, self.y)):
            self.x = random.randrange(0, len(self.layout))
            self.y = random.randrange(0, len(self.layout[0]))

        self.new_x = -1
        self.new_y = -1

    def getPosition(self):
        return [self.x, self.y]

    def getNewPosition(self):
        return [self.new_x, self.new_y]
    
    def getID(self):
        return self.id
    
    def getLayout(self):
        return self.layout
    
    def getHealth(self):
        return self.health
    
    def setHealth(self, new_health):
        self.health = new_health

    def setColor(self, color):
        self.image.fill(color)
        
    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def die(self):
        self.dead = True

    def isDead(self):
        return self.dead


    def update(self, all_agents):
        if (not self.dead):
            if (len(self.plan)>0): #nasty FIXME
                self.new_x = (self.plan[0][0])
                self.new_y = (self.plan[0][1])
                
                for agent in all_agents:
                    if not agent.isDead() and agent.getPosition() == [self.new_x, self.new_y] and not agent.getNewPosition() == [self.x, self.y]:
                        return 

                self.move(dx = (self.new_x - self.x), dy = (self.new_y - self.y))
                self.plan    = self.plan[1:]
                self.rect.x  = self.x * TILESIZE 
                self.rect.y  = self.y * TILESIZE


    def checkAlarm(self, alarm):
        if alarm and not self.danger:
            self.danger     = True
            self.reconsider = True
    

    #O agente so pode ficar em perigo de duas maneiras: ou alguem lhe comunica que ha fogo/fumo ou ele encontra fogo/fumo 
    def receiveMessage(self, message):
        for i in range(len(message)):
            for j in range(len(message[i])):
                if (self.layout[i][j] != message[i][j] and (isFire(message,i,j) or isSmoke(message,i,j))):
                    self.danger       = True
                    self.reconsider   = True
                    self.layout[i][j] = message[i][j]

    def percept(self, layout):
        x0 = self.x-RANGE
        y0 = self.y-RANGE 
        x1 = self.x+RANGE
        y1 = self.y+RANGE
        self.reconsider = False
        if (x0 < 0):
            x0 = 0
        if (y0 < 0):
            y0 = 0
        if (x1 > len(layout)-1):
            x1 = len(layout)-1
        if (y1 > len(layout[0])-1):
            y1 = len(layout[0])-1
        for i in range(x0, x1+1):
            for j in range(y0, y1+1):
                if (self.layout[i][j] != layout[i][j]):
                    self.danger       = True
                    self.reconsider   = True
                    self.layout[i][j] = layout[i][j]


    def moveRandom(self):
        row  = [-1, 0, 0, 1]
        col  = [0, -1, 1, 0]
        move = [True, False]
        prob = [1/self.id, 1-(1/self.id)]
        if (choices(move, prob)):
            i = random.randrange(0, 4)
            x = self.x + row[i]
            y = self.y + col[i]
            if (not isWall(self.layout,x,y) and not isFire(self.layout,x,y) and not isSmoke(self.layout,x,y) and not isExit(self.layout,x,y) and not isAlarm(self.layout,x,y)):
                return [[x, y]]
        return [[self.x, self.y]]


    def plan_(self):
        if (not self.danger):     #anda aleatoriamente por aí
            self.plan = self.moveRandom()
        elif (self.reconsider):   #update nos beliefs dele -> fogo or fumo -> shortest paths
            self.plan = self.Dijkstra()


    #Our reactive agent logic
    def panic(self):
        #procura uma casa adjacente livre. se nao existir uma, procura uma casa com fumo. se nao existir, desiste :(
        row = [-1, 0, 0, 1]
        col = [0, -1, 1, 0]

        # shuffle visiting order of the neighbours
        combined = list(zip(row, col))
        random.shuffle(combined)
        row, col = zip(*combined)
        
        for i in range(len(row)):
            x = self.x + row[i]
            y = self.y + col[i]
            if (not isWall(self.layout,x,y) and not isFire(self.layout,x,y) and not isSmoke(self.layout,x,y) and not isAlarm(self.layout,x,y)):
                return [[x,y]]
        for i in range(len(row)):
            x = self.x + row[i]
            y = self.y + col[i]
            if (isSmoke(self.layout,x,y)):
                return [[x,y]]
        return [[self.x,self.y]] #desisti
    

    def BFS(self):
        source  = [self.x, self.y]
        dests   = self.exits
       	visited = [[0 for _ in range(len(self.layout))] for _ in range(len(self.layout))]
        queue   = []
        path    = []
        prev    = []
        my_dest = []

        if (source in dests):
        	return [source]

        queue.append(source)
        visited[source[0]][source[1]] = 1
        
        row = [-1, 0, 0, 1]
        col = [0, -1, 1, 0]
        
        while (len(queue) > 0):
            cur = queue.pop(0)
            if(cur in dests): 
                my_dest = cur
                break

            # shuffle visiting order of the neighbours
            combined = list(zip(row, col))
            random.shuffle(combined)
            row, col = zip(*combined)

            for i in range(len(row)):
                x = cur[0] + row[i]
                y = cur[1] + col[i]

                if (x < 0 or y < 0 or x >= len(self.layout) or y >= len(self.layout[0])): continue
                if(not isWall(self.layout,x,y) and not isFire(self.layout,x,y) and visited[x][y] == 0 and not isAlarm(self.layout,x,y)):
                    visited[x][y] = 1
                    l = [x, y]
                    queue.append(l)
                    prev.append([l, cur])

        panic = True
        for dest in dests:
            if visited[dest[0]][dest[1]]:
                panic = False

        if panic:
            return self.panic()

        at = my_dest
        while at != source:
            path.append(at)
            for i in range(len(prev)):
                if(at == prev[i][0]): 
                	at = prev[i][1]
        path.reverse()
        return path


    def Dijkstra(self):
        source  = [self.x, self.y]
        dests   = self.exits

        if (source in dests):
            return [source]

        row = [-1, 0, 0, 1]
        col = [0, -1, 1, 0]

        queue   = []
        my_dest = []
        visited = []
        parents  = dict()
        distance = dict()
        enqueued = dict()

        # Initialize stuff
        for i in range(len(self.layout)):
            visit = []
            for j in range(len(self.layout)):
                visit.append(0)
                parents[(i,j)]  = None
                distance[(i,j)] = math.inf
                enqueued[(i,j)] = None
            visited.append(visit)

        queue = [[0, source[0], source[1]]]
        heapq.heapify(queue)
        distance[tuple(source)] = 0
        enqueued[tuple(source)] = True
        visited [source[0]][source[1]] = 1

        while (len(queue) > 0):
            
            cur    = heapq.heappop(queue)
            parent = (cur[1], cur[2])

            if (not enqueued[parent]):
                continue

            enqueued[parent] = False

            if(list(parent) in dests): 
                my_dest = list(parent)
                break

            # shuffle visiting order of the neighbours
            combined = list(zip(row, col))
            random.shuffle(combined)
            row, col = zip(*combined)

            for i in range(len(row)):

                x, y = parent[0] + row[i], parent[1] + col[i]
                if (x < 0 or y < 0 or x >= len(self.layout) or y >= len(self.layout[0])): continue

                if (enqueued[(x,y)] == False ):
                    continue

                if(not isWall(self.layout,x,y) and not isFire(self.layout,x,y) and not isAlarm(self.layout,x,y) and visited[x][y] == 0):
                    visited[x][y] = 1
                    
                    #Compute cost of this transition
                    weight = 1
                    if (isSmoke(self.layout,x,y)):
                        weight += 1-self.risk

                    alternative = distance[parent] + weight

                    if (alternative < distance[(x,y)]):
                        distance[(x,y)] = alternative
                        parents[(x,y)]  = list(parent)
                        heapq.heappush(queue,[alternative, x, y])
                        enqueued[(x,y)] = True

        panic = True
        for dest in dests:
            if visited[dest[0]][dest[1]]:
                panic = False

        if panic:
            return self.panic()

        path = []
        at   = my_dest
        while at != source:
            path.append(at)
            at = parents[tuple(at)]

        path.reverse()
        return path


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x * TILESIZE 
        self.rect.y = self.y * TILESIZE

class Alarm(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image  = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def CheckAlarm(self, layout):
        x0 = self.x - ALARMRANGE
        y0 = self.y - ALARMRANGE 
        x1 = self.x + ALARMRANGE
        y1 = self.y + ALARMRANGE

        for i in range(x0, x1+1):
            for j in range(y0, y1+1):
                if(isSmoke(layout, i, j) or isFire(layout, i, j)): return True
        return False
    
    def FireAlarm(self):
        self.image.fill(RED)


class Fire(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x * TILESIZE 
        self.rect.y = self.y * TILESIZE

class Smoke(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x * TILESIZE 
        self.rect.y = self.y * TILESIZE