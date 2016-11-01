# Modulo: tree_search
# 
# Fornece um conjunto de classes para suporte a resolucao de 
# problemas por pesquisa em arvore:
#    SearchDomain  - dominios de problemas
#    SearchProblem - problemas concretos a resolver 
#    SearchNode    - nos da arvore de pesquisa
#    SearchTree    - arvore de pesquisa, com metodos para 
#                    a respectiva construcao
#
#  (c) Luis Seabra Lopes, Introducao a Inteligencia Artificial

import math


# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain:
    # construtor
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal_state):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return state == self.goal


# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self, state, parent, cost, depth, heuristic):
        self.state = state
        self.parent = parent
        self.cost = cost
        self.depth = depth
        self.heuristic = heuristic

    def __str__(self):
        return '(' + str(self.state) + '; ' + str(self.cost) + '; h:' + str(math.trunc(self.heuristic)) + '; ' + str(
            self.depth) + ')'

    def __repr__(self):
        return self.__str__()


# Arvores de pesquisa
class SearchTree:
    # construtor
    def __init__(self, problem, limit=10):
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, 0,
                          problem.domain.heuristic(problem.initial, problem.goal))
        self.open_nodes = [root]
        self.total_cost = 0
        self.total_depth = 0
        self.limit = limit
        self.number_nodes = 0
        self.iterations = 0

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self, node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path

    def get_total_cost(self):
        return self.total_cost

    # procurar a solucao
    def search(self):
        actions_visited = []
        while True:
            self.iterations += 1
            # print "\niteration: " + str(self.iterations)
            if not self.open_nodes:
                return None
            # print "* open nodes: "
            # print "".join(map(str, self.open_nodes))
            node = self.open_nodes[0]
            # print "* node:\n " + node.__str__()
            if self.problem.goal_test(node.state):
                path = self.get_path(node)
                self.total_cost = node.cost
                self.total_depth = node.depth
                return path
            self.open_nodes[0:1] = []
            actions = self.problem.domain.actions(node.state)
            # print "* actions: "
            # print "".join(map(str, actions))
            lnewnodes = []
            for a in actions:
                if a not in actions_visited:
                    actions_visited += [a]
                    newstate = self.problem.domain.result(node.state, a)
                    newnode = SearchNode(newstate, node,
                                         self.problem.domain.cost(node.state, a) + node.cost,
                                         node.depth + 1,
                                         self.problem.domain.heuristic(newstate, self.problem.goal))

                    lnewnodes += [newnode]
            # print "* lnewnodes: "
            # print "".join(map(str, lnewnodes))
            self.add_to_open(lnewnodes)

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self, lnewnodes):
        self.open_nodes += lnewnodes
        self.open_nodes.sort(key=lambda node: node.cost + node.heuristic)
        # print self.open_nodes