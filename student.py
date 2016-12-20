from snake import Snake
import signal
__author__ = "Daniela Simões, 76771 & Cristiana Carvalho, 77682"


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def distance(state, goal_state):
    # https://en.wikipedia.org/wiki/Taxicab_geometry
    (startx, starty) = state
    (endx, endy) = goal_state
    return abs(endx - startx) + abs(endy - starty)


class NoTimeException(BaseException):
    def __init__(self, message):
        self.message = message


class FoodPosArea:

    def __init__(self, food_pos):
        self.limit = 5
        self.x_minus = food_pos[0]-self.limit
        self.x_plus = food_pos[0]+self.limit
        self.y_minus = food_pos[1]-self.limit
        self.y_plus = food_pos[1]+self.limit
        self.area_center = food_pos
        self.path = []

    def valid(self, food_pos):
        return self.x_minus <= food_pos[0] <= self.x_plus and self.y_minus <= food_pos[1] <= self.y_plus


class StudentPlayer(Snake):
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
        # area food pos
        self.food_area = None
        # tree search
        self.tree_search = None
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

        self.other_head_position = maze.playerpos[0] if self.body[0] != maze.playerpos[0] \
            else maze.playerpos[len(self.body)]

        self.head_collision = {(self.other_head_position[0], self.other_head_position[1] + 1),
                               (self.other_head_position[0], self.other_head_position[1] - 1),
                               (self.other_head_position[0] + 1, self.other_head_position[1]),
                               (self.other_head_position[0] - 1, self.other_head_position[1])}

        # we must limit our think time, and we will limit the time
        # to the tree search return the value
        signal.signal(signal.SIGALRM, self.signal_handler)
        search_time = (self.agent_time / 1000) * (14 / 20)  # 15/20 = 75% # 17/20 = 85%
        signal.setitimer(signal.ITIMER_REAL, search_time)

        previous_search = []  # to use the previous path that we can use
        get_result = True
        preservar_food_area = False
        teleport = False
        initial = self.head_position
        target = self.maze.foodpos

        try:
            # se caminho calculado e comida dentro da food area
            if self.food_area is not None and self.food_area.valid(self.maze.foodpos) and self.food_area.path != []:
                # seguimos o caminho
                # se estivermos muito proximos da comida, vamos diretos à comida
                # iremos iniciar a tree search para a comida e não iremos aproveitar nenhum caminho
                # calculamos a proximidade com a heuristica entre o initial e o target, se for igual a 3
                # usamos a tree search para fazer a pesquisa

                if self.food_area.valid(initial):
                    self.visited_cells = set()
                    problem = SearchProblem(self, initial, target)
                    self.tree_search = SearchTree(problem)
                    self.tree_search.search()
                else:
                    # verificamos se estamos no caminho e escolhemos ir para o ponto imediatemente a seguir
                    # sem calcular a tree search
                    if initial in self.food_area.path:
                        self.result = self.food_area.path[self.food_area.path.index(initial):]
                        # se estiver um player no nosso caminho teremos que verificar !!!
                        # percorrer o nosso result, se estiver um player logo imediatamente a seguir, terá de fazer
                        # um novo search, apagando o path da nossa food area

                        if not self.is_not_player_pos(self.result[1]) or not self.head_collision_avoidance(self.result[1]):
                            self.visited_cells = set()
                            problem = SearchProblem(self, initial, target)
                            self.tree_search = SearchTree(problem)
                            self.tree_search.search()
                        else:
                            print("GET RESULT")
                            get_result = False
                    else:
                        # se não estamos no camiho correto, vamos tentar ir para o ponto inicial do caminho,
                        # descobrindo a tree search para esse ponto
                        target = self.food_area.path[0]
                        self.visited_cells = set()
                        problem = SearchProblem(self, initial, target)
                        self.tree_search = SearchTree(problem)
                        self.tree_search.search()
            elif self.food_area is not None and self.food_area.valid(self.maze.foodpos) and not self.food_area.valid(initial):
                # se o caminho não estiver ainda calculado e a comida estiver dentro da food area
                # reaproveitamos a tree search, e o ponto para onde vamos vai ser a direção para o ponto
                # initial do caminho encontrado

                teleport = True
                preservar_food_area = self.tree_search.search()
                # provavelmente iremos ter teleport, portanto necessário ajuste !!!!
                print(self.name, "TELEPORT")
            elif self.head_position in self.result and self.maze.foodpos in self.result:
                # we will try to use the previous path
                # if the result has the initial point and the goal point
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
                    # print(self.name, "reaproveitei")

                self.visited_cells = set()
                problem = SearchProblem(self, initial, target)
                self.tree_search = SearchTree(problem)
                self.tree_search.search()
            elif initial in self.result:
                # verify if is in food pos

                if self.food_area is not None and self.food_area.valid(self.maze.foodpos):
                    # yes is in food pos
                    tmp = []

                    for cell in self.result[self.result.index(self.head_position)+1:]:
                        if self.is_not_player_pos(cell) and self.head_collision_avoidance(cell):
                            tmp += [cell]
                        else:
                            break

                    if len(tmp) != 0:
                        previous_search = [self.head_position] + tmp[:-1]
                        initial = tmp[-1]

                        if not self.food_area.valid(initial):
                            target = self.food_area.area_center
                        print(self.name, "reaproveitei food area")
                else:
                    print(self.name, "\n\n\n## NEW FOOD AREA\n\n\n")
                    self.food_area = FoodPosArea(self.maze.foodpos)

                self.visited_cells = set()
                problem = SearchProblem(self, initial, target)
                self.tree_search = SearchTree(problem)
                self.tree_search.search()
            else:
                self.visited_cells = set()
                problem = SearchProblem(self, initial, target)
                self.tree_search = SearchTree(problem)
                self.tree_search.search()

            signal.alarm(0)
        except NoTimeException as e:
            pass

        if get_result:
            self.result = previous_search + self.tree_search.get_path(self.node)
        else:
            if self.head_position not in self.result:
                signal.signal(signal.SIGALRM, self.signal_handler)
                search_time = (self.agent_time / 1000) * (5 / 20)  # 15/20 = 75% # 17/20 = 85%
                signal.setitimer(signal.ITIMER_REAL, search_time)

                self.visited_cells = set()
                problem = SearchProblem(self, self.head_position, self.result[0])
                tree_search = SearchTree(problem)

                try:
                    tree_search.search()
                    self.result = tree_search.get_path(self.node)

                    signal.alarm(0)
                except NoTimeException as e:
                    self.result = tree_search.get_path(self.node)
                    pass
            else:
                self.result = self.result[self.result.index(self.head_position):]

        if preservar_food_area:
            print("Preservar food area")
            self.food_area.path = self.result

            if self.head_position not in self.result:
                signal.signal(signal.SIGALRM, self.signal_handler)
                search_time = (self.agent_time / 1000) * (5 / 20)  # 15/20 = 75% # 17/20 = 85%
                signal.setitimer(signal.ITIMER_REAL, search_time)

                self.visited_cells = set()
                problem = SearchProblem(self, self.head_position, self.result[0])
                tree_search = SearchTree(problem)
                try:
                    tree_search.search()
                    self.result = tree_search.get_path(self.node)

                    signal.alarm(0)
                except NoTimeException as e:
                    self.result = tree_search.get_path(self.node)
                    pass
            else:
                self.result = self.result[self.result.index(self.head_position):]
        elif teleport:
            print(self.name, self.head_position, self.result, "HA TELEPORT ou DIAGONAIS")

            if self.head_position not in self.result:
                signal.signal(signal.SIGALRM, self.signal_handler)
                search_time = (self.agent_time / 1000) * (5 / 20)  # 15/20 = 75% # 17/20 = 85%
                signal.setitimer(signal.ITIMER_REAL, search_time)

                print("OLA")
                self.visited_cells = set()
                problem = SearchProblem(self, self.head_position, self.result[0])
                tree_search = SearchTree(problem)
                try:
                    tree_search.search()
                    self.result = tree_search.get_path(self.node)

                    signal.alarm(0)
                except NoTimeException as e:
                    self.result = tree_search.get_path(self.node)
                    pass
            else:
                self.result = self.result[self.result.index(self.head_position):]

        print(self.name, get_result, self.head_position, self.result)

        if len(self.result) > 2:
            if not self.is_not_player_pos(self.result[1]):  # or not self.head_collision_avoidance(self.result[1]):
                # esta la um player
                self.visited_cells = set()
                actions_list = self.actions(initial)
                if len(actions_list) != 0:
                    self.direction = sub(actions_list[0], self.body[0])
            else:
                self.direction = sub(self.result[1], self.head_position)
        elif len(self.result) == 2:
            self.direction = sub(self.result[1], self.head_position)

            food_collision_matrix = [(self.maze.foodpos[0], self.maze.foodpos[1] + 1),
                                     (self.maze.foodpos[0], self.maze.foodpos[1] - 1),
                                     (self.maze.foodpos[0] + 1, self.maze.foodpos[1]),
                                     (self.maze.foodpos[0] - 1, self.maze.foodpos[1])]

            if self.other_head_position in food_collision_matrix and not self.winning_points:
                # running away
                self.visited_cells = set()
                actions_list = self.actions(initial)

                if len(actions_list) != 0:
                    if self.maze.foodpos in actions_list:
                        actions_list.remove(self.maze.foodpos)
                        self.direction = sub(actions_list[0], self.body[0])
        else:
            self.visited_cells = set()
            actions_list = self.actions(initial)

            if len(actions_list) != 0:
                self.direction = sub(actions_list[0], self.body[0])
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

    def heuristic(self, state, goal_state):
        distances = list()

        # real_distance
        distances.append(distance(state, goal_state))

        # go_top_distance
        go_top_distance_point1 = (state[0], self.y_limit)
        go_top_distance_point2 = (state[0], 0)

        if self.is_not_obstacle(go_top_distance_point1) and self.is_not_obstacle(go_top_distance_point2):
            distances.append(distance(state, go_top_distance_point1) +
                             distance(go_top_distance_point2, goal_state))

        # go_bottom_distance
        go_bottom_distance_point1 = (state[0], 0)
        go_bottom_distance_point2 = (state[0], self.y_limit)

        if self.is_not_obstacle(go_bottom_distance_point1) and self.is_not_obstacle(go_bottom_distance_point2):
            distances.append(distance(state, go_bottom_distance_point1) +
                             distance(go_bottom_distance_point2, goal_state))

        # go_left_distance
        go_left_distance_point1 = (0, state[1])
        go_left_distance_point2 = (self.x_limit, state[1])

        if self.is_not_obstacle(go_left_distance_point1) and self.is_not_obstacle(go_left_distance_point2):
            distances.append(distance(state, go_left_distance_point1) +
                             distance(go_left_distance_point2, goal_state))

        # go_right_distance
        go_right_distance_point1 = (self.x_limit, state[1])
        go_right_distance_point2 = (0, state[1])

        if self.is_not_obstacle(go_right_distance_point1) and self.is_not_obstacle(go_right_distance_point2):
            distances.append(distance(state, go_right_distance_point1) +
                             distance(go_right_distance_point2, goal_state))

        return min(distances)


class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return state == self.goal


class SearchNode:
    def __init__(self, state, parent, c, h, f):
        self.state = state
        self.parent = parent
        self.c = c
        self.h = h
        self.f = f


class SearchTree:
    def __init__(self, problem):
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, self.problem.domain.heuristic(self.problem.initial, self.problem.goal), None)
        root.f = root.c + root.h
        self.open_nodes = [root]
        self.result = []
        self.visited = []

    def get_path(self, node):
        if node.parent is None:
            return [node.state]

        return self.get_path(node.parent) + [node.state]

    def search(self):
        while self.open_nodes:
            self.problem.domain.node = self.open_nodes[0]
            self.open_nodes[0:1] = []

            if self.problem.goal_test(self.problem.domain.node.state):
                print("encontrei resultado")
                return True

            if self.problem.domain.node.state in self.visited:
                continue

            self.visited += [self.problem.domain.node.state]
            lnewnodes = []

            list_actions = self.problem.domain.actions(self.problem.domain.node.state)

            if len(list_actions) == 0 and len(self.open_nodes) == 0:
                list_actions = self.problem.domain.actions_survive(self.problem.domain.node.state)

            for newstate in list_actions:
                if newstate not in self.get_path(self.problem.domain.node):
                    cost = 1
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    lnewnodes += [SearchNode(newstate, self.problem.domain.node, self.problem.domain.node.c + cost,
                                             heuristic, self.problem.domain.node.c + cost + heuristic)]

            self.add_to_open(lnewnodes)

        return False

    def add_to_open(self, lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda e: e.f)