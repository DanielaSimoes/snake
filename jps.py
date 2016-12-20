from __future__ import print_function
import itertools, heapq

# Define some constants representing the things that can be in a field.
OBSTACLE = -10
DESTINATION = -2
UNINITIALIZED = -1


class FastPriorityQueue:
    """
    Because I don't need threading, I want a faster queue than queue.PriorityQueue
    Implementation copied from: https://docs.python.org/3.3/library/heapq.html
    """

    def __init__(self):
        self.pq = []  # list of entries arranged in a heap
        self.counter = itertools.count()  # unique sequence count

    def add_task(self, task, priority=0):
        'Add a new task'
        count = next(self.counter)
        entry = [priority, count, task]
        heapq.heappush(self.pq, entry)

    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heapq.heappop(self.pq)
            return task
        raise KeyError('pop from an empty priority queue')

    def empty(self):
        return len(self.pq) == 0


def jps(field, start_x, start_y, end_x, end_y, x_size, y_size):
    """
    Run a jump point search on a field with obstacles.

    Parameters
    field            - 2d array representing the cost to get to that node.
    start_x, start_y - the x, y coordinates of the starting position (must be ints)
    end_x, end_y     - the x, y coordinates of the destination (must be ints)

    Return:
    a list of tuples corresponding to the jump points. drawing straight lines betwen them gives the path.
    OR
    [] if no path is found.
    """

    class FoundPath(Exception):
        """ Raise this when you found a path. it's not really an error,
        but I need to stop the program and pass it up to the real function"""
        pass

    def queue_jumppoint(node):
        """
        Add a jump point to the priority queue to be searched later. The priority is the minimum possible number of steps to the destination.
        Also check whether the search is finished.

        Parameters
        pq - a priority queue for the jump point search
        node - 2-tuple with the coordinates of a point to add.

        Return
        None
        """
        if node is not None:
            pq.add_task(node, field[node[0]][node[1]] + max(abs(node[0] - end_x), abs(node[1] - end_y)))

    def _jps_explore_diagonal(startX, startY, directionX, directionY):
        """
        Explores field along the diagonal direction for JPS, starting at point (startX, startY)

        Parameters
        startX, startY - the coordinates to start exploring from.
        directionX, directionY - an element from: {(1, 1), (-1, 1), (-1, -1), (1, -1)} corresponding to the x and y directions respectively.

        Return
        A 2-tuple containing the coordinates of the jump point if it found one
        None if no jumppoint was found.
        """
        cur_x, cur_y = startX, startY  # indices of current cell.
        curCost = field[startX][startY]

        while (True):
            last_x = cur_x
            last_y = cur_y
            cur_x += directionX
            cur_y += directionY
            curCost += 1

            if cur_x >= x_size:
                return None

            if cur_y >= y_size:
                return None

            if field[last_x+directionX][last_y] == UNINITIALIZED \
                    or field[cur_x][cur_y] == UNINITIALIZED:
                field[last_x+directionX][last_y] = curCost
                sources[last_x+directionX][last_y] = startX, startY

                curCost += 1

                field[cur_x][cur_y] = curCost
                sources[cur_x][cur_y] = startX, startY
            elif field[last_x][last_y+directionY] == UNINITIALIZED \
                    or field[cur_x][cur_y] == UNINITIALIZED:
                field[last_x][last_y+directionY] = curCost
                sources[last_x][last_y+directionY] = startX, startY

                curCost += 1

                field[cur_x][cur_y] = curCost
                sources[cur_x][cur_y] = startX, startY
            elif cur_x == end_x and cur_y == end_y:  # destination found
                field[cur_x][cur_y] = curCost
                sources[cur_x][cur_y] = startX, startY
                raise FoundPath()
            else:  # collided with an obstacle. We are done.
                return None

            # If a jump point is found,
            if (cur_x + directionX) < x_size and field[cur_x + directionX][cur_y] == OBSTACLE \
                    and (cur_y + directionY) < y_size and field[cur_x + directionX][cur_y + directionY] != OBSTACLE:
                return cur_x, cur_y
            else:  # otherwise, extend a horizontal "tendril" to probe the field.
                queue_jumppoint(_jps_explore_cardinal(cur_x, cur_y, directionX, 0))

            if (cur_y + directionY) < y_size and field[cur_x][cur_y + directionY] == OBSTACLE and \
                    (cur_x + directionX) < x_size and field[cur_x + directionX][cur_y + directionY] != OBSTACLE:
                return cur_x, cur_y
            else:  # extend a vertical search to look for anything
                queue_jumppoint(_jps_explore_cardinal(cur_x, cur_y, 0, directionY))

    def _jps_explore_cardinal(startX, startY, directionX, directionY):
        """
        Explores field along a cardinal direction for JPS (north/east/south/west), starting at point (startX, startY)

        Parameters
        startX, startY - the coordinates to start exploring from.
        directionX, directionY - an element from: {(1, 1), (-1, 1), (-1, -1), (1, -1)} corresponding to the x and y directions respectively.

        Result:
        A 2-tuple containing the coordinates of the jump point if it found one
        None if no jumppoint was found.
        """
        cur_x, cur_y = startX, startY  # indices of current cell.
        curCost = field[startX][startY]

        while (True):
            cur_x += directionX
            cur_y += directionY
            curCost += 1

            if cur_x >= len(field[0]):
                return None

            if cur_y >= len(field[1]):
                return None

            if field[cur_x][cur_y] == UNINITIALIZED:
                field[cur_x][cur_y] = curCost
                sources[cur_x][cur_y] = startX, startY
            elif cur_x == end_x and cur_y == end_y:  # destination found
                field[cur_x][cur_y] = curCost
                sources[cur_x][cur_y] = startX, startY
                raise FoundPath()
            else:  # collided with an obstacle or previously explored part. We are done.
                return None

            # check neighbouring cells, i.e. check if cur_x, cur_y is a jump point.
            if directionX == 0:
                if (cur_x + 1) < x_size and field[cur_x + 1][cur_y] == OBSTACLE and \
                        (cur_y + directionY) < y_size and field[cur_x + 1][cur_y + directionY] != OBSTACLE:
                    return cur_x, cur_y
                if field[cur_x - 1][cur_y] == OBSTACLE and field[cur_x - 1][cur_y + directionY] != OBSTACLE:
                    return cur_x, cur_y
            elif directionY == 0:
                if (cur_y + 1) < y_size and (cur_x + directionX) < x_size and field[cur_x][cur_y + 1] == OBSTACLE \
                        and field[cur_x + directionX][cur_y + 1] != OBSTACLE:
                    return cur_x, cur_y
                if (cur_y - 1) >= 0 and (cur_x + directionX) < x_size and field[cur_x][cur_y - 1] == OBSTACLE \
                        and field[cur_x + directionX][cur_y - 1] != OBSTACLE:
                    return cur_x, cur_y

    # MAIN JPS FUNCTION
    field = [[j for j in i] for i in field]  # this takes less time than deep copying.

    # Initialize some arrays and certain elements.
    sources = [[(None, None) for i in field[0]] for j in field]  # the jump-point predecessor to each point.
    field[start_x][start_y] = 0
    field[end_x][end_y] = DESTINATION

    pq = FastPriorityQueue()
    queue_jumppoint((start_x, start_y))

    # Main loop: iterate through the queue
    while (not pq.empty()):
        pX, pY = pq.pop_task()

        try:
            queue_jumppoint(_jps_explore_cardinal(pX, pY, 1, 0))
            queue_jumppoint(_jps_explore_cardinal(pX, pY, -1, 0))
            queue_jumppoint(_jps_explore_cardinal(pX, pY, 0, 1))
            queue_jumppoint(_jps_explore_cardinal(pX, pY, 0, -1))

            queue_jumppoint(_jps_explore_diagonal(pX, pY, 1, 1))
            queue_jumppoint(_jps_explore_diagonal(pX, pY, 1, -1))
            queue_jumppoint(_jps_explore_diagonal(pX, pY, -1, 1))
            queue_jumppoint(_jps_explore_diagonal(pX, pY, -1, -1))
        except FoundPath:
            return get_full_path(_get_path(sources, start_x, start_y, end_x, end_y), field)

    raise ValueError("No path is found")
    # end of jps


def _get_path(sources, start_x, start_y, end_x, end_y):
    """
    Reconstruct the path from the source information as given by jps(...).

    Parameters
    sources          - a 2d array of the predecessor to each node
    start_x, start_y - the x, y coordinates of the starting position
    end_x, end_y     - the x, y coordinates of the destination

    Return
    a list of jump points as 2-tuples (coordinates) starting from the start node and finishing at the end node.
    """
    result = []
    cur_x, cur_y = end_x, end_y

    while cur_x != start_x or cur_y != start_y:
        result.append((cur_x, cur_y))
        cur_x, cur_y = sources[cur_x][cur_y]
    result.reverse()
    return [(start_x, start_y)] + result


def _signum(n):
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0


def get_full_path(path, field):
    """
    Generates the full path from a list of jump points. Assumes that you moved in only one direction between
    jump points.

    Parameters
    path - a path generated by get_path

    Return
    a list of 2-tuples (coordinates) starting from the start node and finishing at the end node.
    """

    if path == []:
        return []

    cur_x, cur_y = path[0]
    result = [(cur_x, cur_y)]
    for i in range(len(path) - 1):
        while cur_x != path[i + 1][0] or cur_y != path[i + 1][1]:
            dir_x = _signum(path[i + 1][0] - path[i][0])
            dir_y = _signum(path[i + 1][1] - path[i][1])

            if abs(dir_x) == 1 and abs(dir_y) == 1:
                if field[cur_x + dir_x][cur_y] != OBSTACLE:
                    result.append((cur_x+dir_x, cur_y))
                elif field[cur_x][cur_y + dir_y] != OBSTACLE:
                    result.append((cur_x, cur_y + dir_y))
                else:
                    print("não é suposto", dir_x, dir_y)

            cur_x += dir_x
            cur_y += dir_y
            result.append((cur_x, cur_y))
    return result
