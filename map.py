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
    def __init__(self, map, agent_time):
        self.map = map
        self.prob = GridConnections(map)
        self.calculated = None
        self.agent_time = agent_time

    def search_path(self, from_point, to):
        prob = SearchProblem(self.prob, from_point, to)
        tree = SearchTree(prob)
        self.calculated = tree.search(self.agent_time)
        return self.calculated

