from math import *


class GridConnections:
    def __init__(self, map):
        # self.connections = map.connections
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
            if i[0] < 0:  # if the map does not continue to the left, snake returns from the right side
                action = (i[0] + self.map.Xsize, i[1])
            elif i[1] < 0:  # if the map does not continue to the top, snake returns from the bottom side
                action = (i[0], i[1] + self.map.Ysize)
            elif i[0] >= self.map.Xsize:  # if the map does not continue to the right, snake returns from the left side
                action = (i[0] % self.map.mapsize[0], i[1])
            elif i[1] >= self.map.Ysize:  # if the map does not continue to the right, snake returns from the left side
                action = (i[0], i[1] % self.map.mapsize[1])
            else:
                action = i

            if action not in self.map.maze.obstacles and action not in self.map.maze.playerpos and \
                            action not in self.visited:
                actlist += [(cell, action)]

        return actlist

    def result(self, state, action):
        (C1, C2) = action
        if C1 == state:
            return C2
        elif C2 == state:
            return C1

    def cost(self, state, action):
        return 0

    def heuristic(self, state, goal_state):
        return self.coordinates[
            self.to_index(state, self.map.mapsize[1]), self.to_index(goal_state, self.map.mapsize[1])]

    def to_index(self, point, mapsize_y):
        return point[0] * mapsize_y + point[1]


class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return state == self.goal


class SearchNode:
    def __init__(self, state, parent, c=None, h=None, f=None):
        self.state = state
        self.parent = parent
        self.c = c
        self.h = h
        self.f = f


class SearchTree:
    def __init__(self, problem):
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, \
                          self.problem.domain.heuristic(self.problem.initial, self.problem.goal))
        root.f = root.c + root.h
        self.open_nodes = [root]
        self.result = []

    def get_path(self, node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return (path)

    def search(self):
        visited = []

        max_iterations = 100
        i = 0

        while self.open_nodes != []:
            i += 1
            node = self.open_nodes[0]
            self.open_nodes[0:1] = []
            if self.problem.goal_test(node.state):
                self.result = self.get_path(node)
                return self.result
            if node.state in visited:
                continue
            visited += [node.state]
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state, a)
                if newstate not in self.get_path(node):
                    cost = self.problem.domain.cost(node.state, a)
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    lnewnodes += [SearchNode(newstate, node, node.c + cost, heuristic, \
                                             node.c + cost + heuristic)]
            self.add_to_open(lnewnodes)

            if i > max_iterations:
                self.result = self.get_path(node)
                return self.result

        return []

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.f)
