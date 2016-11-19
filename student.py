from snake import Snake
from tree_search import Map, Way, sub, add


class Student(Snake):
    def __init__(self, body=[(0, 0)], direction=(1, 0), name="DC"):
        """
        :var self.agent_time: The agent time is the time that the time that we have to think
        :var self.map: our knowledge about the map game
        :var self.maze: the maze the we receive in the updateDirection
        :var self.dist_to_walk: 1 we will only look 1 cell at cell
        :var self.winning_points: if we have more points than the other agent
        """
        self.map = None
        self.agent_time = None
        self.dist_to_walk = 1
        self.winning_points = False
        self.old_direction = (0, 0)
        super().__init__(body, direction, name=name)

    def update(self, points=None, mapsize=None, count=None, agent_time=None):
        """
        This is the first method call when the game starts, we will receive the points, mapsize, count and agent_time.
        :param points: list of tuples, each entry has name, points.
        :param mapsize: tuple (x,y) sizes; map size will be static since the game starts
        :param count: iterations of the game
        :param agent_time: our time to think
        :return: nothing.
        """
        self.agent_time = agent_time  # save the agent time to further usage
        self.winning_points = points[1][1] < points[0][1] if points[0][0] == self.name else points[0][1] < points[1][1]

        if self.map is None:
            self.map = Map(map_size=mapsize)

    def updateDirection(self, maze):
        head_position = self.body[0]

        other_head_position = maze.playerpos[0] if head_position != maze.playerpos[0] \
            else maze.playerpos[len(self.body)]

        # usar matrix
        maze.obstacles += [(other_head_position[0], other_head_position[1]+1),
                           (other_head_position[0], other_head_position[1]-1),
                           (other_head_position[0]+1, other_head_position[1]),
                           (other_head_position[0]-1, other_head_position[1])]
        self.map.update(maze=maze)
        way = Way(self.map, self.agent_time, self.dist_to_walk)
        path = way.search_path(head_position, maze.foodpos)

        """
        The path is not none, we have path and the path as length > 2,
        the path is a list of cells, which cell is a tuple of X, Y.
        The first entry of the path is the head position, the last is the
        food pos if the path to the food take the normal time to be calculated.
        """
        if len(path) > 1:
            self.old_direction = self.direction
            self.direction = sub(path[1], head_position)
        else:
            way.problem.visited = []
            actions = way.problem.actions(head_position)

            if len(actions) > 0:
                self.direction = sub(way.problem.actions(head_position)[0], head_position)
            else:
                print(self.name, "no path")
            # print(path[1], head_position, self.direction)
            # print(self.name, self.direction, self.old_direction, len(path))
"""
            actions = way.problem.actions(head_position)
            if len(actions) == 0:
                # go die wherever you want anyway
                return

            ###### BETA LOGIC ######

            If the other player is close to the food we must avoid the food.

            ###### BETA LOGIC ######
            positions_around_food = [(maze.foodpos[0] + self.dist_to_walk, maze.foodpos[1]),
                                     (maze.foodpos[0] - self.dist_to_walk, maze.foodpos[1]),
                                     (maze.foodpos[0], maze.foodpos[1] + self.dist_to_walk),
                                     (maze.foodpos[0], maze.foodpos[1] - self.dist_to_walk)]

            actions = way.problem.actions(head_position, visited_condition=False)

            other_player = [item for item in maze.playerpos if item not in self.body]

            if other_player[0] in positions_around_food:
                if self.winning_points:

                    # run away, quit on food, else, I'll loose
                    try:
                        actions_to_run = actions.remove((head_position, maze.foodpos))
                    except ValueError:
                        actions_to_run = actions

                    if len(actions_to_run) != 0:
                        self.direction = sub(actions_to_run[0][1], head_position)
                        return
            if len(path) == 2:
                self.direction = sub(path[1], head_position)
            else:
                print("########")
                print(self.name + ": NO PATH" + str(path))
                print("########")
                self.direction = sub(actions[0][1], head_position)
"""