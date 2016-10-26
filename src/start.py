from game import *
from human import HumanSnake
from agent1 import Agent1
from student import Student

#start the game
if __name__ == "__main__":
    snake=SnakeGame(hor=60, ver=30, fps=20)
    snake.setObstacles(15) #level of obstacles
    snake.setPlayers([  
        Agent1([snake.playerPos()]),
        Student([snake.playerPos()]),
    ])
    snake.start()
