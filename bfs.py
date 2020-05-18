import numpy as np
map = []

def bfs(source, dest):        # [x,y] -> source | [x,y] -> destination
    visited = [[0 for _ in range(len(map))] for _ in range(len(map))]
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

            if (x < 0 or y < 0 or x >= len(map) or y >= len(map)): continue
            if(map[x][y] != 'W' and visited[x][y] == 0):
                visited[x][y] = 1
                list = []
                list.append(x)
                list.append(y)
                queue.append(list)

                p = []
                p.append(list)
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



f = open( 'maze.txt' , 'r').read()
map = [item.split() for item in f.split('\n')[:-1]]
#print(np.array(map))

#p = bfs([17,16], [6,9])
#print(p)
