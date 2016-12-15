import signal
import numpy as np
import itertools
import scipy.spatial.distance as d


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


class AgentBrain:
    """
    Our interpretation of the game, the obstacles, distances, and limits.
    The maze given by the game is stored here.
    """
    def __init__(self, map_size, agent_time, name, winning_points):
        self.obstacles = None
        self.head_collision_matrix = None
        self.body = None
        self.agent_time = agent_time
        self.name = name
        self.direction = (0, 0)
        self.winning_points = winning_points
        self.other_head_position = (0,0)

        self.x_size = map_size[0]
        self.y_size = map_size[1]
        self.x_limit = map_size[0]-1
        self.y_limit = map_size[1]-1

        self.maze = None

        cords = list(itertools.product(np.arange(self.x_size), np.arange(self.y_size)))
        cords = np.array(cords)
        self.distance = d.cdist(cords, cords)

        self.visited = []
        self.dist_to_walk = 1

    def update(self, maze=None, body=None):
        if maze is not None:
            self.maze = maze

        if body is not None:
            self.body = body

        if self.maze is not None:
            self.obstacles = np.matrix(self.maze.obstacles+self.maze.playerpos)

            self.other_head_position = maze.playerpos[0] if self.body[0] != maze.playerpos[0] \
                else maze.playerpos[len(self.body)]

            self.head_collision_matrix = np.matrix([(self.other_head_position[0], self.other_head_position[1]+1),
                                                   (self.other_head_position[0], self.other_head_position[1]-1),
                                                   (self.other_head_position[0]+1, self.other_head_position[1]),
                                                   (self.other_head_position[0]-1, self.other_head_position[1])])

    def get_direction(self, from_point, to):
        self.visited = []
        tree = SearchTree(self, from_point, to)
        return tree.search()

    def actions(self, cell, avoidance=True):
        self.visited += [cell]
        actlist = []

        options = [(cell[0], cell[1] + self.dist_to_walk), (cell[0], cell[1] - self.dist_to_walk),
                   (cell[0] + self.dist_to_walk, cell[1]), (cell[0] - self.dist_to_walk, cell[1])]

        for i in options:
            if i[0] < 0:
                # if the agent_brain does not continue to the left, snake returns from the right side
                action = (i[0] + self.x_size, i[1])
            elif i[1] < 0:
                # if the agent_brain does not continue to the top, snake returns from the bottom side
                action = (i[0], i[1] + self.y_size)
            elif i[0] >= self.x_size:
                # if the agent_brain does not continue to the right, snake returns from the left side
                action = (i[0] % self.x_size, i[1])
            elif i[1] >= self.y_size:
                # if the agent_brain does not continue to the right, snake returns from the left side
                action = (i[0], i[1] % self.y_size)
            else:
                action = i

            if avoidance and action not in self.visited and self.is_not_obstacle(action) and \
                    self.head_collision_avoidance(action):
                actlist += [action]
            elif not avoidance and self.is_not_obstacle(action):
                actlist += [action]

        return actlist

    def heuristic(self, state, goal_state):
        goal_state_index = self.to_index(goal_state)
        state_index = self.to_index(state)

        real_distance = self.distance[state_index, goal_state_index]

        go_top_distance = self.distance[state_index, self.to_index((state[0], self.y_limit))]
        go_top_distance += self.distance[self.to_index((state[0], 0)), goal_state_index]

        go_bottom_distance = self.distance[state_index, self.to_index((state[0], 0))]
        go_bottom_distance += self.distance[self.to_index((state[0], self.y_limit)), goal_state_index]

        go_left_distance = self.distance[state_index, self.to_index((0, state[1]))]
        go_left_distance += self.distance[self.to_index((self.x_limit, state[1])), goal_state_index]

        go_right_distance = self.distance[state_index, self.to_index((self.x_limit, state[1]))]
        go_right_distance += self.distance[self.to_index((0, state[1])), goal_state_index]

        return min(real_distance, go_top_distance, go_bottom_distance, go_left_distance, go_right_distance)

    def to_index(self, point):
        return point[0] * self.y_size + point[1]

    def is_not_obstacle(self, cell):
        result = np.where((self.obstacles == cell).all(axis=1))
        return not (len(result[0]) and len(result[1]))

    def head_collision_avoidance(self, cell):
        result = np.where((self.head_collision_matrix == cell).all(axis=1))
        return not (len(result[0]) and len(result[1]))


class SearchNode:
    def __init__(self, state, parent, h=None):
        self.state = state
        self.parent = parent
        self.h = h
        self.node = None

    def __repr__(self):
        return str(self.state)

    def __str__(self):
        return str(self.state)


class SearchTree:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
        root = SearchNode(initial, None, self.domain.heuristic(self.initial, self.goal))
        self.open_nodes = [root]
        self.result = []
        self.node = root
        # TO TEST
        self.actions = []

    def get_path(self, node):
        if node.parent is None:
            return [node.state]

        return self.get_path(node.parent) + [node.state]

    def goal_test(self, state):
        return state == self.goal

    def search_helper(self):
        visited = []

        # max_iteration = 10
        # iteration = 0

        while self.open_nodes:
            self.node = self.open_nodes[0]
            self.open_nodes[0:1] = []

            self.result = self.get_path(self.node)

            if self.goal_test(self.node.state):
                signal.alarm(0)
                return

            if self.node.state in visited:
                continue

            visited += [self.node.state]
            lnewnodes = []

            self.actions = self.domain.actions(self.node.state)

            if len(self.actions) == 0 and len(self.open_nodes) == 0:
                print("avoidance")
                self.actions = self.domain.actions(self.node.state, avoidance=False)
            # elif len(actions) == 0:
            #   print("ELSE", self.problem.domain.name, self.problem.goal, self.problem.initial, self.open_nodes)

            for newstate in self.actions:
                if newstate not in self.result:
                    heuristic = self.domain.heuristic(newstate, self.goal)
                    lnewnodes += [SearchNode(newstate, self.node, heuristic)]
            self.add_to_open(lnewnodes)

        signal.alarm(0)

    def signal_handler(self, signum, frame):
        raise Exception("Timed out!")

    def search(self):
        signal.signal(signal.SIGALRM, self.signal_handler)
        agent_time = (self.domain.agent_time/1000)*(4/5)

        signal.setitimer(signal.ITIMER_REAL, agent_time)

        try:
            self.search_helper()
            signal.alarm(0)
        except Exception:
            pass

        # get the direction
        direction = self.domain.direction

        if len(self.result) > 2:
            direction = sub(self.result[1], self.domain.body[0])
        elif len(self.result) == 2:
            direction = sub(self.result[1], self.domain.body[0])

            food_collision_matrix = [(self.domain.maze.foodpos[0], self.domain.maze.foodpos[1] + 1),
                                     (self.domain.maze.foodpos[0], self.domain.maze.foodpos[1] - 1),
                                     (self.domain.maze.foodpos[0] + 1, self.domain.maze.foodpos[1]),
                                     (self.domain.maze.foodpos[0] - 1, self.domain.maze.foodpos[1])]

            if self.domain.other_head_position in food_collision_matrix and not self.domain.winning_points:  # running away
                self.visited = []
                actions = self.domain.actions(self.node.state)
                if self.domain.maze.foodpos in actions:
                    actions = actions.remove(self.domain.maze.foodpos)
                    direction = sub(actions[0], self.domain.body[0])

        if direction[0] > 1 or direction[0] < -1:
            direction = -int(self.domain.x_size * 1.0 / direction[0]), direction[1]
        if direction[1] > 1 or direction[1] < -1:
            direction = direction[0], -int(self.domain.y_size * 1.0 / (direction[1]))

        self.domain.direction = direction

        return direction

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.h)
