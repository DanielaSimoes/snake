from snake import Snake
import signal
from jps import *
__author__ = "Daniela Simões, 76771 & Cristiana Carvalho, 77682"

OBSTACLE = -10
DESTINATION = -2
UNINITIALIZED = -1


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
        self.other_head_position = (0,0)
        # direction
        self.direction = direction
        # cell size step
        self.dist_to_walk = 1
        # avoid collision
        self.head_collision = None
        # path result
        self.result = []
        #
        self.field = []
        self.obstacles_parsed = False
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
            self.field = [[UNINITIALIZED for x in range(mapsize[1])] for y in range(mapsize[0])]
            # now we will save the limits of the map
            self.x_limit = mapsize[0]-1
            self.y_limit = mapsize[1]-1
            # x and y size
            self.x_size = mapsize[0]
            self.y_size = mapsize[1]

    def updateDirection(self, maze):
        self.head_position = self.body[0]

        print("xsize, ysize", self.x_size, self.y_size)

        if not self.obstacles_parsed:
            for x, y in maze.obstacles:
                self.field[x][y] = OBSTACLE

            self.obstacles_parsed = True

        current_field = self.field

        for x, y in maze.playerpos:
            current_field[x][y] = OBSTACLE

        self.result = jps(self.field, self.head_position[0], self.head_position[1],
                          maze.foodpos[0], maze.foodpos[1], self.x_size, self.y_size)

        print(self.result)

        if len(self.result) >= 2:
            self.direction = sub(self.result[1], self.head_position)
        else:
            print("NAO DEVIA ACONTECER 1")

        if self.direction[0] > 1 or self.direction[0] < -1:
            self.direction = -int(self.x_size * 1.0 / self.direction[0]), self.direction[1]

        if self.direction[1] > 1 or self.direction[1] < -1:
            self.direction = self.direction[0], -int(self.y_size * 1.0 / (self.direction[1]))