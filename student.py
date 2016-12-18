from snake import Snake
import scipy.spatial.distance as d
import numpy as np
import itertools
import signal


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


class NoTimeException(BaseException):
    def __init__(self, message):
        self.message = message


class Student(Snake):
    def __init__(self, body=[(0, 0)], direction=(0, 0), name="DC"):
        self.agent_time = None
        self.winning_points = False
        # distances array
        self.distances = None
        # map limits and sizes
        self.x_limit = 0
        self.y_limit = 0
        self.y_size = 0
        self.x_size = 0
        # position of our snake head
        self.head_position = body[0]
        # direction
        self.direction = direction
        # store maze for domain
        self.maze = None
        # visited cells list
        self.visited_cells = set()
        # cell size step
        self.dist_to_walk = 1
        # node of tree search
        self.node = None
        super().__init__(body, direction, name=name)

    def signal_handler(self, signum, frame):
        raise NoTimeException("Timed out!")

    def update(self, points=None, mapsize=None, count=None, agent_time=None):
        # save the agent time to further usage
        self.agent_time = agent_time

        # if we have more points than the other snake
        self.winning_points = points[1][1] < points[0][1] if points[0][0] == self.name \
            else points[0][1] < points[1][1]

        # if distances is None and mapsize is not None we can instantiate the distance_array
        if self.distances is None and mapsize is not None:
            cords = np.array(list(itertools.product(np.arange(mapsize[0]), np.arange(mapsize[1]))))
            self.distances = d.cdist(cords, cords)

            # now we will save the limits of the map
            self.x_limit = mapsize[0]-1
            self.y_limit = mapsize[1]-1
            # x and y size
            self.x_size = mapsize[0]
            self.y_size = mapsize[1]

    def updateDirection(self, maze):
        self.head_position = self.body[0]
        self.maze = maze

        # we must limit our think time, and we will limit the time
        # to the tree search return the value
        signal.signal(signal.SIGALRM, self.signal_handler)
        search_time = (self.agent_time / 1000) * (15 / 20)  # 15/20 = 75%
        signal.setitimer(signal.ITIMER_REAL, search_time)

        self.visited_cells = set()
        problem = SearchProblem(self, self.head_position, self.maze.foodpos)

        try:
            tree_search = SearchTree(problem)
            tree_search.search()
        except NoTimeException as e:
            pass

        result = problem.domain.get_path(self.node)

        if len(result) >= 2:
            self.direction = sub(result[1], self.head_position)
        else:
            print("NAO DEVIA ACONTECER")
            
    def actions(self, cell):
        if cell in self.visited_cells:
            print("NAO DEVIA ACONTECER")

        self.visited_cells.add(cell)
        actlist = []

        options = [(cell[0], cell[1] + self.dist_to_walk), (cell[0], cell[1] - self.dist_to_walk),
                   (cell[0] + self.dist_to_walk, cell[1]), (cell[0] - self.dist_to_walk, cell[1])]

        for option in options:
            if option[0] < 0:
                # if the agent_brain does not continue to the left, snake returns from the right side
                action = (option[0] + self.x_size, option[1])
            elif option[1] < 0:
                # if the agent_brain does not continue to the top, snake returns from the bottom side
                action = (option[0], option[1] + self.y_size)
            elif option[0] >= self.x_size:
                # if the agent_brain does not continue to the right, snake returns from the left side
                action = (option[0] % self.x_size, option[1])
            elif option[1] >= self.y_size:
                # if the agent_brain does not continue to the right, snake returns from the left side
                action = (option[0], option[1] % self.y_size)
            else:
                action = option

            if action not in self.visited_cells and self.is_not_obstacle(action) and self.is_not_player_pos(action):
                actlist += [action]

        return actlist

    def is_not_obstacle(self, cell):
        return not (cell in self.maze.obstacles)

    def is_not_player_pos(self, cell):
        return not (cell in self.maze.playerpos)

    def to_index(self, cell):
        return cell[0] * self.y_size + cell[1]

    def heuristic(self, state, goal_state):
        return self.distances[self.to_index(goal_state), self.to_index(state)]

    def result(self, state, action):
        c1, c2 = action

        if c1 == state:
            return c2
        elif c2 == state:
            return c1


class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return state == self.goal


class SearchNode:
    def __init__(self,state, parent, h):
        self.state = state
        self.parent = parent
        self.h = h


class SearchTree:
    def __init__(self, problem):
        self.problem = problem
        self.open_nodes = [SearchNode(problem.initial, None,
                                      self.problem.domain.heuristic(self.problem.initial, self.problem.goal))]
        self.result = []

    def get_path(self, node):
        if node.parent is None:
            return [node.state]

        return self.get_path(node.parent) + [node.state]

    def search(self):
        visited = []

        while self.open_nodes:
            self.problem.domain.node = self.open_nodes[0]
            self.open_nodes[0:1] = []

            if self.problem.goal_test(self.problem.domain.node.state):
                return self.result

            if self.problem.domain.node.state in visited:
                continue

            visited += [self.problem.domain.node.state]
            lnewnodes = []

            for a in self.problem.domain.actions(self.problem.domain.node.state):
                newstate = self.problem.domain.result(self.problem.domain.node.state, a)
                if newstate not in self.get_path(self.problem.domain.node):
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    lnewnodes += [SearchNode(newstate, self.problem.domain.node, heuristic)]
            self.add_to_open(lnewnodes)

        return []

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.h)
