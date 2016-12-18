from snake import Snake
import signal
__author__ = "Daniela Simões, 76771 & Cristiana Carvalho, 77682"


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
        # avoid collision
        self.head_collision = None
        # path result
        self.result = []
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
        if self.x_limit == 0 and mapsize is not None:
            # now we will save the limits of the map
            self.x_limit = mapsize[0] - 1
            self.y_limit = mapsize[1] - 1
            # x and y size
            self.x_size = mapsize[0]
            self.y_size = mapsize[1]

    def updateDirection(self, maze):
        self.head_position = self.body[0]
        self.maze = maze

        other_head_position = maze.playerpos[0] if self.body[0] != maze.playerpos[0] \
            else maze.playerpos[len(self.body)]

        self.head_collision = {(other_head_position[0], other_head_position[1] + 1),
                               (other_head_position[0], other_head_position[1] - 1),
                               (other_head_position[0] + 1, other_head_position[1]),
                               (other_head_position[0] - 1, other_head_position[1])}

        # we must limit our think time, and we will limit the time
        # to the tree search return the value
        signal.signal(signal.SIGALRM, self.signal_handler)
        search_time = (self.agent_time / 1000) * (15 / 20)  # 15/20 = 75% # 17/20 = 85%
        signal.setitimer(signal.ITIMER_REAL, search_time)

        tree_search = None  # only for code proposes
        previous_search = []  # to use the previous path that we can use

        try:
            self.visited_cells = set()
            initial = self.head_position

            # we will try to use the previous path
            # if the resulthas the initial point and the goal point
            if self.head_position in self.result and self.maze.foodpos in self.result:
                # we have to verify if the path that we can take advantage have an
                # player or head collision avoidance
                tmp = []

                for cell in self.result[self.result.index(self.head_position)+1:self.result.index(self.maze.foodpos)+1]:
                    if self.is_not_player_pos(cell) and self.head_collision_avoidance(cell):
                        tmp += [cell]
                    else:
                        break

                if len(tmp) != 0:
                    previous_search = [self.head_position] + tmp[:-1]
                    initial = tmp[-1]
                    print(self.name, "reaproveitei")

            problem = SearchProblem(self, initial, self.maze.foodpos)
            tree_search = SearchTree(problem)
            tree_search.search()
            signal.alarm(0)
        except NoTimeException as e:
            pass

        self.result = previous_search + tree_search.get_path(self.node)

        if len(self.result) >= 2:
            self.direction = sub(self.result[1], self.head_position)
        else:
            print("NAO DEVIA ACONTECER 1")

        if self.direction[0] > 1 or self.direction[0] < -1:
            self.direction = -int(self.x_size * 1.0 / self.direction[0]), self.direction[1]

        if self.direction[1] > 1 or self.direction[1] < -1:
            self.direction = self.direction[0], -int(self.y_size * 1.0 / (self.direction[1]))

    def actions(self, cell):
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

            if action not in self.visited_cells and self.is_not_obstacle(action) and self.is_not_player_pos(action) \
                    and self.head_collision_avoidance(action):
                actlist += [action]

        return actlist

    def actions_survive(self, cell):
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

            if action not in self.visited_cells and self.is_not_obstacle(action) \
                    and self.head_collision_avoidance(action):
                actlist += [action]

        return actlist

    def is_not_obstacle(self, cell):
        return cell not in self.maze.obstacles

    def is_not_player_pos(self, cell):
        return cell not in self.maze.playerpos

    def head_collision_avoidance(self, cell):
        return cell not in self.head_collision

    def distance(self, state, goal_state):
        return ((state[0] - goal_state[0]) ** 2 + (state[1] - goal_state[1]) ** 2) ** 0.5

    def heuristic(self, state, goal_state):
        distances = list()

        # real_distance
        distances.append(self.distance(state, goal_state))

        # go_top_distance
        go_top_distance_point1 = (state[0], self.y_limit)
        go_top_distance_point2 = (state[0], 0)

        if self.is_not_obstacle(go_top_distance_point1) and self.is_not_obstacle(go_top_distance_point2):
            distances.append(self.distance(state, go_top_distance_point1) +
                             self.distance(go_top_distance_point2, goal_state))

        # go_bottom_distance
        go_bottom_distance_point1 = (state[0], 0)
        go_bottom_distance_point2 = (state[0], self.y_limit)

        if self.is_not_obstacle(go_bottom_distance_point1) and self.is_not_obstacle(go_bottom_distance_point2):
            distances.append(self.distance(state, go_bottom_distance_point1) +
                             self.distance(go_bottom_distance_point2, goal_state))

        # go_left_distance
        go_left_distance_point1 = (0, state[1])
        go_left_distance_point2 = (self.x_limit, state[1])

        if self.is_not_obstacle(go_left_distance_point1) and self.is_not_obstacle(go_left_distance_point2):
            distances.append(self.distance(state, go_left_distance_point1) +
                             self.distance(go_left_distance_point2, goal_state))

        # go_right_distance
        go_right_distance_point1 = (self.x_limit, state[1])
        go_right_distance_point2 = (0, state[1])

        if self.is_not_obstacle(go_right_distance_point1) and self.is_not_obstacle(go_right_distance_point2):
            distances.append(self.distance(state, go_right_distance_point1) +
                             self.distance(go_right_distance_point2, goal_state))

        return min(distances)


class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return state == self.goal


class SearchNode:
    def __init__(self, state, parent, h):
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

            list_actions = self.problem.domain.actions(self.problem.domain.node.state)

            if len(list_actions) == 0 and len(self.open_nodes) == 0:
                list_actions = self.problem.domain.actions_survive(self.problem.domain.node.state)

            for newstate in list_actions:
                if newstate not in self.get_path(self.problem.domain.node):
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    lnewnodes += [SearchNode(newstate, self.problem.domain.node, heuristic)]

            self.add_to_open(lnewnodes)

        return []

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.h)
