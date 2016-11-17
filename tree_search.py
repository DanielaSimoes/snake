import signal
import numpy as np
import itertools
import scipy.spatial.distance as d


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


class Map:
    def __init__(self, map_size, body):
        self.coordinates = None
        self.x_size = map_size[0]
        self.y_size = map_size[1]
        self.maze = None
        self.body = None
        self.other_player = []
        self.together = False

        self.update(body=body)
        self.instance()

    def update(self, body=None, maze=None):
        if maze is not None:
            self.maze = maze

        if body is not None:
            self.body = body  # our agent body
            # since the maze is updated in the second call in the updateDirection
            # we don't have to verify if the maze is None
            if self.maze is not None:
                self.other_player = [item for item in self.maze.playerpos if item not in self.body]

                # some logic to see if the other agent is around us (beta)
                result = sub(body[0], self.other_player[0])
                result = (abs(result[0]), abs(result[1]))
                self.together = (result[0] == 1 or result[1] == 1)

    def instance(self):
        cords = np.array(list(itertools.product(np.arange(self.x_size), np.arange(self.y_size))))
        self.coordinates = d.cdist(cords, cords)


class Way:
    def __init__(self, current_map, agent_time, dist_to_walk,):
        self.current_map = current_map
        self.problem = GridConnections(current_map, dist_to_walk)
        self.calculated = None
        self.agent_time = agent_time

    def search_path(self, from_point, to):
        tree = SearchTree(SearchProblem(self.problem, from_point, to))
        self.calculated = tree.search(self.agent_time)
        return self.calculated


class GridConnections:
    def __init__(self, map, dist_to_walk):
        # self.connections = map.connections
        self.coordinates = map.coordinates
        self.map = map
        self.visited = []
        self.dist_to_walk = dist_to_walk

        if map.together and len(map.other_player) >= 2:
            other_player_head = map.other_player[0]
            next_head = map.other_player[1]
            self.other_player = [add(other_player_head, sub(other_player_head, next_head))]
        else:
            self.other_player = []

    def actions(self, cell, visited_condition=True):
        self.visited += [cell]
        actlist = []

        options = [(cell[0], cell[1] + self.dist_to_walk), (cell[0], cell[1] - self.dist_to_walk),
                   (cell[0] + self.dist_to_walk, cell[1]), (cell[0] - self.dist_to_walk, cell[1])]

        for i in options:
            if i[0] < 0:  # if the map does not continue to the left, snake returns from the right side
                action = (i[0] + self.map.x_size, i[1])
            elif i[1] < 0:  # if the map does not continue to the top, snake returns from the bottom side
                action = (i[0], i[1] + self.map.y_size)
            elif i[0] >= self.map.x_size:  # if the map does not continue to the right, snake returns from the left side
                action = (i[0] % self.map.x_size, i[1])
            elif i[1] >= self.map.y_size:  # if the map does not continue to the right, snake returns from the left side
                action = (i[0], i[1] % self.map.y_size)
            else:
                action = i

            if visited_condition and action not in self.map.maze.obstacles and action not in self.map.maze.playerpos \
                    and action not in self.visited and action not in self.other_player:
                actlist += [(cell, action)]
            elif not visited_condition and action not in self.map.maze.obstacles \
                    and action not in self.map.maze.playerpos and action not in self.other_player:
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
            self.to_index(state, self.map.y_size), self.to_index(goal_state, self.map.y_size)]

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
            result = self.search_helper()
            signal.alarm(0)
            return result
        except Exception:
            # print("SAFOU")
            signal.alarm(0)
            self.result = self.get_path(self.node)
            return self.result

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.f)
