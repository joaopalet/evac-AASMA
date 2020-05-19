# Sprites

import pygame
from settings import *



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, walls, layout, fires):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.walls  = walls
        self.layout = layout
        self.fires  = fires

    def move(self, dx=0, dy=0):
        if not self.collide_with_walls(dx, dy):
            self.x += dx
            self.y += dy
    
    def collide_with_walls(self, dx=0, dy=0):
        for wall in self.walls:
            if wall.x == self.x + dx and wall.y == self.y + dy:
                return True
        return False
    
    def update(self):
        self.rect.x = self.x * TILESIZE 
        self.rect.y = self.y * TILESIZE

    def bfs(self, source, dest):        # [x,y] -> source | [x,y] -> destination
        visited = [[0 for _ in range(len(self.layout))] for _ in range(len(self.layout))]
        queue = []
        path = []
        prev = []
        queue.append(source)

        visited[source[0]][source[1]] = 1
        
        row = [-1, 0, 0, 1]
        col = [0, -1, 1, 0]
        
        while (len(queue) > 0):
            cur = queue.pop(0)
            if(cur == dest): break

            for i in range(len(row)):
                x = cur[0] + row[i]
                y = cur[1] + col[i]

                if (x < 0 or y < 0 or x >= len(self.layout) or y >= len(self.layout)): continue
                if(self.layout[x][y] != 'W' and self.layout[x][y] != 'F' and visited[x][y] == 0):
                    visited[x][y] = 1
                    l = [x, y]
                    queue.append(l)

                    p = []
                    p.append(l)
                    p.append(cur)
                    prev.append(p)              # prev = [ [no, predecessor] ]

        at = dest
        while at != source:
            path.append(at)
            for i in range(len(prev)):
                if(at == prev[i][0]): at = prev[i][1]
        path.append(source)
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