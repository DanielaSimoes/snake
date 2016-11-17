from snake import Snake
from constants import *
from tree_search import Map, Way


class Student(Snake):
    def __init__(self, body=[(0, 0)], direction=(1, 0), name="DC"):
        # criar um mapa
        self.map = None
        self.maze = None
        self.agent_time = None
        self.dist_to_walk = 1
        self.game_points = (0,0)
        super().__init__(body, direction, name=name)

    def sub(self, a, b):
        return a[0] - b[0], a[1] - b[1]

    def update(self, points=None, mapsize=None, count=None,agent_time=None):
        self.agent_time = agent_time
        self.game_points = (points[1][1], points[0][1]) if points[0][0] == self.name else (points[0][1], points[1][1])

        if self.map is None:
            self.map = Map(mapsize, self.maze, self.body)
        else:
            self.map.updateMapBody(mapsize, self.body)

    def updateDirection(self, maze):
        position = self.body[0]

        self.map.updateMaze(maze)
        way = Way(self.map, self.agent_time, self.dist_to_walk)
        path = way.search_path(position, maze.foodpos)

        if path is not None and len(path) > 2:
            self.direction = self.sub(path[1], position)

        else:
            actions = way.prob.actions(position)
            if len(actions) == 0:
                # go die wherever you want anyway
                return

            positions_around_food = [(maze.foodpos[0] + self.dist_to_walk, maze.foodpos[1]),
                                     (maze.foodpos[0] - self.dist_to_walk, maze.foodpos[1]),
                                     (maze.foodpos[0], maze.foodpos[1] + self.dist_to_walk),
                                     (maze.foodpos[0], maze.foodpos[1] - self.dist_to_walk)]

            if path is not None and len(path) >= 2:
                self.direction = self.sub(path[1], position)

                if (len(self.body)== 1 and self.direction == (-1,0)):
                    actions1 = way.prob.actions(position)
                    actions = actions1[1:]
                    self.direction = self.sub(actions[0][1], position)

                elif (len(self.body)== 1 and self.direction == (1,0)):
                    actions1 = way.prob.actions(position)
                    actions = [actions1[0]] + actions1[2:]
                    self.direction = self.sub(actions[0][1], position)

                elif (len(self.body)== 1 and self.direction == (0,1)):
                    actions1 = way.prob.actions(position)
                    actions = [actions1[0]] + [actions1[1]] + actions1[3:]
                    self.direction = self.sub(actions[0][1], position)

                elif (len(self.body)== 1 and self.direction == (0,-1)):
                    actions1 = way.prob.actions(position)
                    actions = [actions1[0]] + [actions1[1]] + actions1[3:]
                    self.direction = self.sub(actions[0][1], position)

            else:
                actions = way.prob.actions(position)


            other_player = [item for item in maze.playerpos if item not in self.body]

            if other_player[0] in positions_around_food:
                if self.game_points[1] < self.game_points[0]:

                    # run away, quit on food, else, I'll loose
                    try:
                        actions_to_run = actions.remove((position, maze.foodpos))
                    except ValueError:
                        actions_to_run = actions

                    if len(actions_to_run) != 0:
                        self.direction = self.sub(actions_to_run[0][1], position)
                        return

            if len(path) == 2:
                self.direction = self.sub(path[1], position)
            else:
                print("########")
                print(self.name + ": NO PATH")
                print("########")
                self.direction = self.sub(actions[0][1], position)

                self.direction = self.sub(actions[0][1], position)


