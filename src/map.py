import numpy as np
import itertools
import scipy.spatial.distance as d
from tree_search import *

class Map:
    def __init__(self, mapsize, maze, body):
        #self.connections = []
        self.coordinates = None
        self.mapsize = mapsize
        self.Xsize = mapsize[0]
        self.Ysize = mapsize[1]
        self.maze = maze
        self.body = body
        self.instance()

    def update(self, mapsize, maze, body):
        self.mapsize = mapsize
        self.maze = maze
        self.body = body

    def updateMaze(self, maze):
        self.maze = maze

    def updateMapBody(self, mapsize, body):
        self.mapsize = mapsize
        self.body = body

    def pathlen(self, a, b):
        return int(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5)

    def instance(self):
        Xpts = np.arange(self.Xsize)
        Ypts = np.arange(self.Ysize)
        coords = np.array(list(itertools.product(Xpts, Ypts)))
        self.coordinates = d.cdist(coords, coords)



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
        #self.connections = map.connections
        self.coordinates = map.coordinates
        self.map = map
        self.visited = []
        self.dist_to_walk = 1

    def actions(self, cell):
        self.visited += [cell]
        actlist = []

        options = [(cell[0], cell[1] + self.dist_to_walk), (cell[0], cell[1] - self.dist_to_walk),
                   (cell[0] + self.dist_to_walk, cell[1]), (cell[0] - self.dist_to_walk, cell[1])]

        for i in options:
            if i[0]<0:  # if the map does not continue to the left, snake returns from the right side
                action = (i[0] + self.map.Xsize, i[1])
            elif i[1] < 0:  # if the map does not continue to the top, snake returns from the bottom side
                action = (i[0], i[1] + self.map.Ysize)
            elif i[0] >= self.map.Xsize: # if the map does not continue to the right, snake returns from the left side
                action = (i[0]%self.map.mapsize[0], i[1])
            elif i[1] >= self.map.Ysize: # if the map does not continue to the right, snake returns from the left side
                action = (i[0], i[1] % self.map.mapsize[1])
            else:
                action = i

            if action not in self.map.maze.obstacles and action not in self.map.maze.playerpos and \
                            action not in self.visited:
                    actlist += [(cell, action)]

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