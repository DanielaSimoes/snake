import signal
import numpy as np
import itertools
import scipy.spatial.distance as d
import time


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def get_path(node):
    if node.parent is None:
        return [node.state]

    return get_path(node.parent) + [node.state]


class NoTimeException(BaseException):
    def __init__(self, message):
        self.message = message


class AgentBrain:
    """
    Our interpretation of the game, the walls, distances, and limits.
    The maze given by the game is stored here.
    """
    def __init__(self, map_size, agent_time, name, winning_points):
        self.walls = None
        self.player_pos = None
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
        self.heuristic_distances = {}

        self.visited = []
        self.dist_to_walk = 1

        # search tree
        self.domain = None
        self.initial = None
        self.goal = None
        self.open_nodes = []
        self.result = []
        self.node = None
        self.actions = []

    def get_actions(self, cell, avoidance=True):
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
        # start = time.time()
        if (state, goal_state) in self.heuristic_distances:
            # end = time.time()
            # print("1:", end - start)
            return self.heuristic_distances[(state, goal_state)]
        elif (goal_state, state) in self.heuristic_distances:
            # end = time.time()
            # print("2:", end - start)
            return self.heuristic_distances[(goal_state, state)]
        else:
            goal_state_index = self.to_index(goal_state)
            state_index = self.to_index(state)

            distances = list()

            # real_distance
            distances.append(self.distance[state_index, goal_state_index])

            # go_top_distance
            go_top_distance_point1 = (state[0], self.y_limit)
            go_top_distance_point2 = (state[0], 0)

            if self.is_not_wall(go_top_distance_point1) and \
                    self.is_not_wall(go_top_distance_point2):
                distances.append(self.distance[state_index, self.to_index(go_top_distance_point1)] +
                                 self.distance[self.to_index(go_top_distance_point2), goal_state_index])

            # go_bottom_distance
            go_bottom_distance_point1 = (state[0], 0)
            go_bottom_distance_point2 = (state[0], self.y_limit)

            if self.is_not_wall(go_bottom_distance_point1) and \
                    self.is_not_wall(go_bottom_distance_point2):
                distances.append(self.distance[state_index, self.to_index(go_bottom_distance_point1)] +
                                 self.distance[self.to_index(go_bottom_distance_point2), goal_state_index])

            # go_left_distance
            go_left_distance_point1 = (0, state[1])
            go_left_distance_point2 = (self.x_limit, state[1])

            if self.is_not_wall(go_left_distance_point1) and \
                    self.is_not_wall(go_left_distance_point2):
                distances.append(self.distance[state_index, self.to_index(go_left_distance_point1)] +
                                 self.distance[self.to_index(go_left_distance_point2), goal_state_index])

            # go_right_distance
            go_right_distance_point1 = (self.x_limit, state[1])
            go_right_distance_point2 = (0, state[1])

            if self.is_not_wall(go_right_distance_point1) and \
                    self.is_not_wall(go_right_distance_point2):
                distances.append(self.distance[state_index, self.to_index(go_right_distance_point1)] +
                                 self.distance[self.to_index(go_right_distance_point2), goal_state_index])

            self.heuristic_distances[(state, goal_state)] = min(distances)
            # end = time.time()
            # print("#:", end - start)
            return self.heuristic_distances[(state, goal_state)]

    def to_index(self, point):
        return point[0] * self.y_size + point[1]

    def is_not_obstacle(self, cell):
        return not (cell in self.walls or cell in self.player_pos)

    def is_not_player(self, cell):
        return not (cell in self.player_pos)

    def is_not_wall(self, cell):
        return not (cell in self.walls)

    def head_collision_avoidance(self, cell):
        return cell not in self.head_collision_matrix

    """
    TREE SEARCH
    """
    def goal_test(self, state):
        return state == self.goal

    def search_helper(self):
        visited = []
        start = time.time()

        # max_iteration = 10
        # iteration = 0

        while self.open_nodes:
            self.node = self.open_nodes[0]
            self.open_nodes[0:1] = []

            if self.goal_test(self.node.state):
                signal.alarm(0)
                return

            if self.node.state in visited:
                continue

            visited += [self.node.state]
            lnewnodes = []

            self.actions = self.get_actions(self.node.state)

            if len(self.actions) == 0 and len(self.open_nodes) == 0:
                self.actions = self.get_actions(self.node.state, avoidance=False)
            # elif len(actions) == 0:
            #   print("ELSE", self.problem.name, self.problem.goal, self.problem.initial, self.open_nodes)

            for newstate in self.actions:
                if newstate not in self.result:
                    heuristic = self.heuristic(newstate, self.goal)
                    lnewnodes += [SearchNode(newstate, self.node, heuristic)]
            self.add_to_open(lnewnodes)

        end = time.time()
        print(self.name, int(round((end - start) * 1000)))
        signal.alarm(0)

    def signal_handler(self, signum, frame):
        raise NoTimeException("Timed out!")

    def get_direction(self, maze, body, from_point, to):
        # print(self.agent_time)
        signal.signal(signal.SIGALRM, self.signal_handler)
        search_time = (self.agent_time/1000)*(16/20)
        signal.setitimer(signal.ITIMER_REAL, search_time)

        """
        UDPATE INFO
        """
        if maze is not None:
            self.maze = maze

        if body is not None:
            self.body = body

        if self.maze is not None:
            self.walls = set(self.maze.obstacles)
            self.player_pos = set(self.maze.playerpos)

            self.other_head_position = maze.playerpos[0] if self.body[0] != maze.playerpos[0] \
                else maze.playerpos[len(self.body)]

            self.head_collision_matrix = {(self.other_head_position[0], self.other_head_position[1] + 1),
                                          (self.other_head_position[0], self.other_head_position[1] - 1),
                                          (self.other_head_position[0] + 1, self.other_head_position[1]),
                                          (self.other_head_position[0] - 1, self.other_head_position[1])}

        if from_point is not None:
            self.initial = from_point

        if to is not None:
            self.goal = to

        """
        INIT SEARCH
        """

        self.visited = []

        # if initial in self.result:
        #     aval = sub(self.result[-1], goal)
        #     print(abs(aval[0]) == 1 or abs(aval[1]) == 1)

        # verify if the result has the initial point
        if self.initial in self.result and self.goal in self.result:
            # we have the path from the initial to the goal state
            tmp = []

#           print("initial: ", initial, " goal: ", goal)
            for cell in self.result[self.result.index(self.initial)+1:self.result.index(self.goal)+1]:
                if self.is_not_player(cell):
                    tmp += [cell]
                else:
                    break

            if len(tmp) == 0:
                self.result = []
                self.initial = self.initial
            else:
                self.result = [self.initial] + tmp[:-1]
                self.initial = tmp[-1]

#           print("self.result antes: ", tmp, self.result, self.initial)
        else:
            # reset
            self.result = []
            # reset

        root = SearchNode(self.initial, None, self.heuristic(self.initial, self.goal))
        self.open_nodes = [root]
        self.node = root
        self.actions = []

        try:
            self.search_helper()
            signal.alarm(0)
        except NoTimeException as e:
            pass

        self.result += get_path(self.node)

#       print(self.result)

        # get the previous direction
        direction = self.direction

        # time
        signal.signal(signal.SIGALRM, self.signal_handler)
        release_time = (self.agent_time/1000)*(2/20)
        signal.setitimer(signal.ITIMER_REAL, release_time)

        try:
            if len(self.result) > 2:
                direction = sub(self.result[1], self.body[0])
            elif len(self.result) == 2:
                direction = sub(self.result[1], self.body[0])

                food_collision_matrix = [(self.maze.foodpos[0], self.maze.foodpos[1] + 1),
                                         (self.maze.foodpos[0], self.maze.foodpos[1] - 1),
                                         (self.maze.foodpos[0] + 1, self.maze.foodpos[1]),
                                         (self.maze.foodpos[0] - 1, self.maze.foodpos[1])]

                if self.other_head_position in food_collision_matrix and not self.winning_points:
                    # running away
                    self.visited = []
                    actions = self.get_actions(self.node.state)
                    if self.maze.foodpos in actions:
                        actions = actions.remove(self.maze.foodpos)
                        direction = sub(actions[0], self.body[0])

            if direction[0] > 1 or direction[0] < -1:
                direction = -int(self.x_size * 1.0 / direction[0]), direction[1]
            if direction[1] > 1 or direction[1] < -1:
                direction = direction[0], -int(self.y_size * 1.0 / (direction[1]))

            self.direction = direction

            signal.alarm(0)
            return direction
        except NoTimeException as e:
            self.direction = direction
            return direction

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.h)


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
