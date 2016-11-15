# python script to test the commit, save the time and the score with the commit
import json
import subprocess

from game import *
from agent1 import Agent1
from student import Student


def get_git_commit_hash():
    return subprocess.check_output(['git', 'describe', '--always'])


def main():
    inputfile = None
    visual = False

    snake = SnakeGame(hor=60, ver=40, fps=20, visual=visual)
    snake.setObstacles(15, inputfile)
    snake.setPlayers([
        Agent1([snake.playerPos()]),
        Student([snake.playerPos()]),
    ])
    snake.start()


def store(stats, entries):
    with open('data.json') as data_file:
        data = json.load(data_file)

    commit = get_git_commit_hash()

    for row in data:
        if row["commit"] == commit:
            data.remove(row)
            data.append({
                "commit": commit,
                "stats": stats,
                "entries": entries
            })
            break

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    main()
