import numpy as np
import itertools
import scipy.spatial.distance as d
from tree_search import *

class Map:
    def __init__(self, mapsize, maze):
        self.connections = []
        self.coordinates = None
        self.mapsize = mapsize
        self.Xsize = mapsize[0]
        self.Ysize = mapsize[1]
        self.maze = maze
        self.dist_to_walk = 1
        self.instance()

    def update(self, mapsize, maze, body):
        #start guide: the old position of the player will be added and the new position will be deleted
        #adversario maze.playerpos[0]
        #our snake : body
        print(self.connections)
        #print(any([body[0] in self.connections[1]]))
        if any([body in self.connections[1]]):
            self.connections.remove(self, body)
            print("PASEI")


    def pathlen(self, a, b):
        return int(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5)

    def instance(self):
        Xpts = np.arange(self.Xsize)
        Ypts = np.arange(self.Ysize)
        coords = np.array(list(itertools.product(Xpts, Ypts)))
        self.coordinates = d.cdist(coords, coords)

        # adicionar as conexoes
        for x,y in coords:
            if (x,y) not in self.maze.obstacles:
                options = [(x, y + self.dist_to_walk), (x, y - self.dist_to_walk), (x + self.dist_to_walk, y), (x - self.dist_to_walk, y)]

                for i in options:
                    if i not in self.maze.obstacles:
                        if i[0]<0:  # if the map does not continue to the left, snake returns from the right side
                            self.connections += [((x, y), (i[0] + self.Xsize, i[1]))]
                        elif i[1] < 0:  # if the map does not continue to the top, snake returns from the bottom side
                            self.connections += [((x, y), (i[0], i[1] + self.Ysize))]
                        elif i[0] > self.Xsize: # if the map does not continue to the right, snake returns from the left side
                            self.connections += [((x,y), (i[0]%self.mapsize[0], i[1]))]
                        elif i[1] > self.Ysize: # if the map does not continue to the right, snake returns from the left side
                            self.connections += [((x, y), (i[0], i[1] % self.mapsize[1]))]
                        else:
                            self.connections += [((x, y), i)]



class Way:
    def __init__(self, map):
        self.map = map
        self.prob = GridConnections(map)
        self.calculated = None

    def search_path(self, from_point, to):
        prob = SearchProblem(self.prob, from_point, to)
        tree = SearchTree(prob)
        self.calculated = tree.search()
        return self.calculated


class GridConnections(SearchDomain):
    def __init__(self, map):
        SearchDomain.__init__(self)
        self.connections = map.connections
        self.coordinates = map.coordinates
        self.map = map
        self.visited = []

    def actions(self, cell):
        self.visited += [cell]
        actlist = []
        for c1, c2 in self.connections:
            if c1 == cell and c2 not in self.visited:
                actlist += [(c1, c2)]
            elif c2 == cell and c1 not in self.visited:
                actlist += [(c2, c1)]
        return actlist

    def result(self, state, action):
        c1, c2 = action
        if c1 == state:
            return c2

    def cost(self, state, action):
        return 0

    def heuristic(self, state, goal_state):
        return self.coordinates[self.to_index(state, self.map.mapsize[1]), self.to_index(goal_state, self.map.mapsize[1])]

    def to_index(self, point, mapsize_y):
        return point[0] * mapsize_y + point[1]