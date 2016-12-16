from snake import Snake
from agent_brain import AgentBrain


class Student(Snake):
    def __init__(self, body=[(0, 0)], direction=(1, 0), name="DC"):
        """
        :var self.agent_time: The agent time is the time that the time that we have to think
        :var self.agent_brain: our knowledge about the agent_brain game
        :var self.maze: the maze the we receive in the updateDirection
        :var self.dist_to_walk: 1 we will only look 1 cell at cell
        :var self.winning_points: if we have more points than the other agent
        """
        self.agent_brain = None
        self.agent_time = None
        self.winning_points = False
        self.old_direction = (0, 0)
        super().__init__(body, direction, name=name)

    def update(self, points=None, mapsize=None, count=None, agent_time=None):
        """
        This is the first method call when the game starts, we will receive the points, mapsize, count and agent_time.
        :param points: list of tuples, each entry has name, points.
        :param mapsize: tuple (x,y) sizes; agent_brain size will be static since the game starts
        :param count: iterations of the game
        :param agent_time: our time to think
        :return: nothing.
        """
        self.agent_time = agent_time  # save the agent time to further usage
        self.winning_points = points[1][1] < points[0][1] if points[0][0] == self.name else points[0][1] < points[1][1]

        if self.agent_brain is None:
            self.agent_brain = AgentBrain(map_size=mapsize, agent_time=agent_time, name=self.name, winning_points=self.winning_points)

    def updateDirection(self, maze):
        head_position = self.body[0]

        self.direction = self.agent_brain.get_direction(maze=maze, body=self.body, from_point=head_position, to=maze.foodpos)
