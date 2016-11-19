import signal
import numpy as np
import itertools
import scipy.spatial.distance as d


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


class Map:
    def __init__(self, map_size):
        self.obstacles = None
        self.distance = None
        self.x_size = map_size[0]
        self.y_size = map_size[1]
        self.x_limit = map_size[0]-1
        self.y_limit = map_size[1]-1
        self.maze = None

        self.instance()

    def update(self, maze=None):
        if maze is not None:
            self.maze = maze

        if self.maze is not None:
            self.obstacles = np.matrix(self.maze.obstacles+self.maze.playerpos)

    def instance(self):
        cords = list(itertools.product(np.arange(self.x_size), np.arange(self.y_size)))
        cords = np.array(cords)
        self.distance = d.cdist(cords, cords)

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
        self.map = map
        self.visited = []
        self.dist_to_walk = dist_to_walk

    def actions(self, cell):
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

            if action not in self.visited and self.cell_valid(action):
                actlist += [action]

        return actlist

    def heuristic(self, state, goal_state):
        goal_state_index = self.to_index(goal_state)
        state_index = self.to_index(state)

        real_distance = self.map.distance[state_index,
                                          goal_state_index]

        go_top_distance = self.map.distance[state_index,
                                            self.to_index((state[0], self.map.y_limit))]
        go_top_distance += self.map.distance[self.to_index((state[0], 0)),
                                             goal_state_index]

        go_bottom_distance = self.map.distance[state_index,
                                               self.to_index((state[0], 0))]
        go_bottom_distance += self.map.distance[self.to_index((state[0], self.map.y_limit)),
                                                goal_state_index]

        go_left_distance = self.map.distance[state_index,
                                             self.to_index((0, state[1]))]
        go_left_distance += self.map.distance[self.to_index((self.map.x_limit, state[1])),
                                              goal_state_index]

        go_right_distance = self.map.distance[state_index,
                                              self.to_index((self.map.x_limit, state[1]))]
        go_right_distance += self.map.distance[self.to_index((0, state[1])),
                                               goal_state_index]

        return min(real_distance, go_top_distance, go_bottom_distance, go_left_distance, go_right_distance)

    def to_index(self, point):
        return point[0] * self.map.y_size + point[1]

    def cell_valid(self, cell):
        result = np.where((self.map.obstacles == cell).all(axis=1))
        return not (len(result[0]) and len(result[1]))


class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return state == self.goal


class SearchNode:
    def __init__(self, state, parent, h=None):
        self.state = state
        self.parent = parent
        self.h = h
        self.node = None


class SearchTree:
    def __init__(self, problem):
        self.problem = problem
        root = SearchNode(problem.initial, None, self.problem.domain.heuristic(self.problem.initial, self.problem.goal))
        self.open_nodes = [root]
        self.result = []

    def get_path(self, node):
        if node.parent is None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path

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
            for newstate in self.problem.domain.actions(self.node.state):
                if newstate not in self.get_path(self.node):
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    lnewnodes += [SearchNode(newstate, self.node, heuristic)]
            self.add_to_open(lnewnodes)

        signal.alarm(0)
        return []

    def signal_handler(self, signum, frame):
        raise Exception("Timed out!")

    def search(self, agent_time):
        signal.signal(signal.SIGALRM, self.signal_handler)
        agent_time = (agent_time/1000)*(3/5)
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
        self.open_nodes.sort(key=lambda e: e.h)
