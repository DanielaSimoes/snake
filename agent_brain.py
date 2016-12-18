import numpy as np
import itertools
import scipy.spatial.distance as d
import time
from math import sqrt


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


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
        self.other_head_position = (0, 0)
        self.execution_time = 0
        self.last_execution_time = 0

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
        self.start = None

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
        # return self.distance[self.to_index(goal_state), self.to_index(state)]
        """
        (x1,y1) = state
        (x2,y2) = goal_state
        return sqrt( (x1-x2)**2 + (y1-y2)**2 )
        """
        if (state, goal_state) in self.heuristic_distances:
            return self.heuristic_distances[(state, goal_state)]
        elif (goal_state, state) in self.heuristic_distances:
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

    def time(self, point):
        self.last_execution_time = self.execution_time
        self.execution_time += (time.time() - self.start) * 1000
        self.start = time.time()

        if self.execution_time >= self.agent_time * 0.80:
            return True
        return False

    def verify(self):
        self.execution_time += (time.time() - self.start) * 1000
        if self.execution_time >= self.agent_time:
            raise Exception(self.execution_time, self.last_execution_time)
        self.start = time.time()

    def search_helper(self):
        visited = []

        # max_iteration = 10
        # iteration = 0

        while self.open_nodes:
            self.get_path(self.node)

            if self.time("1"):
                return

            self.node = self.open_nodes[0]
            self.open_nodes[0:1] = []

            if self.goal_test(self.node.state):
                return

            if self.node.state in visited:
                continue

            visited += [self.node.state]
            lnewnodes = []

            self.actions = self.get_actions(self.node.state)

            if len(self.actions) == 0 and len(self.open_nodes) == 0:
                self.actions = self.get_actions(self.node.state, avoidance=False)

            for newstate in self.actions:
                if self.time("2"):
                    return

                if newstate not in self.get_path(self.node):
                    if self.time("3"):
                        return
                    heuristic = self.heuristic(newstate, self.goal)
                    lnewnodes += [SearchNode(newstate, self.node, heuristic)]
                    if self.time("4"):
                        return

            if self.time("5"):
                return
            self.add_to_open(lnewnodes)

    def get_path(self, node):
        if self.time("125"):
            return self.result

        path = []

        while node.parent is not None:
            path = [node.state] + path
            node = node.parent

            if self.time("126"):
                return self.result

        self.result = [node.state] + path
        return self.result

    def get_direction(self, maze, body, from_point, to):
        # print(self.agent_time)
        self.execution_time = 0
        self.start = time.time()

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
        previous_search = []

        # if initial in self.result:
        #     aval = sub(self.result[-1], goal)
        #     print(abs(aval[0]) == 1 or abs(aval[1]) == 1)

        # verify if the result has the initial point
        if self.initial in self.result and self.goal in self.result:
            # we have the path from the initial to the goal state
            tmp = []

#           print("initial: ", initial, " goal: ", goal)
            for cell in self.result[self.result.index(self.initial)+1:self.result.index(self.goal)+1]:
                if self.is_not_player(cell) and self.head_collision_avoidance(cell):
                    tmp += [cell]
                else:
                    break

            if len(tmp) != 0:
                previous_search = [self.initial] + tmp[:-1]
                self.initial = tmp[-1]

#           print("self.result antes: ", tmp, self.result, self.initial)

        root = SearchNode(self.initial, None, self.heuristic(self.initial, self.goal))
        self.open_nodes = [root]
        self.node = root
        self.actions = []

        self.time("7")
        self.search_helper()
        self.verify()

        self.result = previous_search + self.result

#       print(self.result)

        self.verify()
        # get the previous direction
        direction = self.direction
        self.verify()

        if self.execution_time >= self.agent_time:
            print(self.name, self.execution_time)

        self.verify()

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

        self.verify()
        if direction[0] > 1 or direction[0] < -1:
            direction = -int(self.x_size * 1.0 / direction[0]), direction[1]
        if direction[1] > 1 or direction[1] < -1:
            direction = direction[0], -int(self.y_size * 1.0 / (direction[1]))

        self.direction = direction
        self.verify()

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
