import numpy as np 
from random import randint

class GameSim():
    symbols = {
        0: "x ",
        1: "# ",
        2: "$ ",
        3: "@ ",
        "separator": ". "
    }
    actions = {
        0: lambda x, y: (x, y-1),
        1: lambda x, y: (x+1, y),
        2: lambda x, y: (x, y+1),
        3: lambda x, y: (x-1, y), 
    }

    def __init__(self, shape=(15, 12), max_cap=5):
        self.max_cap = max_cap
        self.id_to_pos = {}
        self.id_to_base = {}
        self.id_to_point = {}
        self.portal_to = {}
        self.cached_picks = set()
        self.shape = shape
        self.bag = np.zeros(shape=shape, dtype=np.int8)
        self.base = np.zeros(shape=shape, dtype=np.int8)
        self.players = np.zeros(shape=shape, dtype=np.int8)
        self.dimonds = np.zeros(shape=shape, dtype=np.int8)
        self.portals = np.zeros(shape=shape, dtype=np.int8)
        self.game_ticks = 0

    def __repr__(self):
        stack = [self.players, self.base, self.dimonds, self.portals]
        rep = ""
        for y in range(self.shape[1]):
            for x in range(self.shape[0]):
                for i, p in enumerate(stack):
                    if p[x,y] != 0:
                        rep += GameSim.symbols[i]
                        break
                else:
                    rep += GameSim.symbols["separator"]
            rep += "\n"
        return rep

    def get_players(self):
        return self.id_to_pos.keys()

    def clear_obj(self):
        self.bag.fill(0)
        self.base.fill(0)
        self.players.fill(0)
        self.dimonds.fill(0)
        self.portals.fill(0)
        self.cached_picks = set()
        self.portal_to = {}
        self.game_ticks = 0
        
    def new_game(self, nb_plyers=1, nb_diamoinds=20, nb_portals=2):
        self.clear_obj()
        self.id_to_pos = {p: self.random_pos(*self.shape) for p in range(nb_plyers)}
        self.id_to_base = {p: self.id_to_pos[p] for p in range(nb_plyers)}
        self.id_to_point = {p: 0 for p in range(nb_plyers)}

        for players, (x,y) in self.id_to_pos.items():
            self.base[x][y] = 1
            self.players[x][y] = 1
        portals = [self.random_pos(*self.shape) for _ in range(nb_portals)]
        for i, (x,y) in enumerate(portals):
            self.portals[x][y] = 1
            self.portal_to[(x,y)]= portals[(i+1)%nb_portals]
        
        for x,y in (self.random_pos(*self.shape) for _ in range(nb_diamoinds)):
            self.dimonds[x][y] = 1

    def get_state(self, id):
        current_player = np.copy(self.players)
        current_player[self.id_to_pos[id]] = 2
        current_base = np.copy(self.base)
        current_base[self.id_to_base[id]] = 2
        return np.stack([current_player, current_base, self.bag, self.dimonds, self.portals])

    def update(self, id, action):
        _from = self.id_to_pos[id]
        _to = GameSim.actions[action](*_from)
        if self.valid(id, *_to):
            self.move(id, _from, _to)
            return True
        return False

    def move(self, id, _from, _to):
        curr_bag = self.bag[_from] + self.dimonds[_to]
        if curr_bag < self.max_cap:
            self.bag[_to] = curr_bag
            self.dimonds[_to] = 0
        else:
            self.bag[_to] = self.bag[_from]
        self.bag[_from] = 0
        
        self.players[self.id_to_pos[id]] = 0
        if _to in self.portal_to:
            self.id_to_pos[id] = self.portal_to[_to]
        else:
            self.id_to_pos[id] = _to
        self.players[self.id_to_pos[id]] = 1

        if self.id_to_pos[id] == self.id_to_base[id]:
            self.id_to_point[id] += self.bag[_to]
            self.bag[_to] = 0
        
        self.game_ticks += 1




    def valid(self, id, x, y):
        if x < 0 or x >= self.shape[0]:
            return False

        if y < 0 or y >= self.shape[1]:
            return False

        for _id, (_x, _y) in self.id_to_base.items():
            if _id == id:
                continue
            if x == _x and y == _y:
                return False

        dest_x, dest_y = -1, -1

        if (x,y) in self.portal_to:
            dest_x, dest_y = self.portal_to[x,y]

        for _id, (_x, _y) in self.id_to_pos.items():
            if _id == id:
                continue
            print(_x, _y)
            if x == _x and y == _y:
                return False
            if dest_x == _x and dest_y == _y:
                return False

        return True
        

    def random_pos(self, x, y):
        pos = randint(0, x-1), randint(0, y-1)
        while pos in self.cached_picks:
            pos = randint(0, x-1), randint(0, y-1)
        self.cached_picks.add(pos)
        return pos