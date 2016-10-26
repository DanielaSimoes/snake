class Map:
    def __init__(self, mapsize, maze):
        self.connections = []
        self.coordinates = {}
        self.mapsize = mapsize
        self.maze = maze
        self.dist_to_walk = 1
        self.instance()

    def update(self, mapsize, maze):
        if mapsize != self.mapsize:
            print("mudou")

        print("ok")

    def pathlen(self, a, b):
        return int(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5)

    def instance(self):
        for x in range(0,self.mapsize[0]):
            for y in range(0, self.mapsize[1]):
                init_x = 0
                init_y = 0
                if (x,y) not in self.coordinates:
                    self.coordinates[(x,y)] = dict()

                for x_to in range(init_x,self.mapsize[0]):
                    for y_to in range(init_y, self.mapsize[1]):
                        dist = self.pathlen((x,y), (x_to,y_to))
                        self.coordinates[(x,y)][(x_to,y_to)] = dist

                        if( y_to < self.mapsize[0] and x_to < self.mapsize[1]):
                            self.coordinates[(x,y)][(y_to,x_to)] = dist

                        if (y < self.mapsize[1]):
                            init_y += 1
                    if (x < self.mapsize[0]):
                        init_x += 1



        # adicionar as conexoes

        for i in range(0, self.mapsize[0]*self.mapsize[1]):
            if (x,y) not in self.maze.obstacles:
                options = [(x, y + self.dist_to_walk), (x, y - self.dist_to_walk), (x + self.dist_to_walk, y), (x - self.dist_to_walk, y)]

                for i in options:
                    if i not in self.maze.obstacles:
                        self.connections += [((x,y),i)] # as lista de conexoes e um tuplo com duas coordenadas: onde estou e onde posso ir
        print("sai")







