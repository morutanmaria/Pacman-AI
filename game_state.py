
class SimulatedState:
    def __init__(self, player_tile, ghost_tiles, maze, pellets_left, energizers_left):
        self.player_tile = player_tile
        self.ghost_tiles = ghost_tiles 
        self.maze = maze
        self.pellets_left = pellets_left 
        self.energizers_left = energizers_left 

    def is_terminal(self):
        if self.player_tile in self.ghost_tiles:
            return True
        if not self.pellets_left and not self.energizers_left:
            return True
        return False
