from math import *
import signal


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

        options1 = [(cell[0], cell[1] + self.dist_to_walk), (cell[0], cell[1] - self.dist_to_walk),
                   (cell[0] + self.dist_to_walk, cell[1])]

        if(len(self.map.body) == 1):
            for i in options1:
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
                    actlist +=[(cell, action)]

        else:
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
        self.node = None


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

    def search_helper(self):
        visited = []

        while self.open_nodes != []:
            self.node = self.open_nodes[0]
            self.open_nodes[0:1] = []

            if self.problem.goal_test(self.node.state):
                self.result = self.get_path(self.node)
                signal.alarm(0)
                return self.result

            if self.node.state in visited:
                continue
            visited += [self.node.state]
            lnewnodes = []
            for a in self.problem.domain.actions(self.node.state):
                newstate = self.problem.domain.result(self.node.state, a)
                if newstate not in self.get_path(self.node):
                    cost = self.problem.domain.cost(self.node.state, a)
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    lnewnodes += [SearchNode(newstate, self.node, self.node.c + cost, heuristic, \
                                             self.node.c + cost + heuristic)]
            self.add_to_open(lnewnodes)

        signal.alarm(0)
        return []

    def signal_handler(self, signum, frame):
        raise Exception("Timed out!")

    def search(self, agent_time):
        signal.signal(signal.SIGALRM, self.signal_handler)
        agent_time = (agent_time/1000)*(3/4)
        self.result = None
        signal.setitimer(signal.ITIMER_REAL, agent_time)

        try:
            return self.search_helper()
        except Exception:
            # print("SAFOU")
            signal.alarm(0)
            self.result = self.get_path(self.node)
            return self.result

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.f)
