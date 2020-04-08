import math

# Speeds
sprinting = 5.6
minecart = 8.0
minecart_diag = math.sqrt(2) * minecart
boat_ice = 40.0
boat_blue_ice = 70.0


class Coord:
    def __init__(self, *args, dim: int = 0):
        if len(args) == 2:
            self.x = args[0]
            self.y = None
            self.z = args[1]
        elif len(args) == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        else:
            raise ValueError('Coord must have 2-3 coordinate values')

        if dim not in [-1, 0, 1]:
            raise ValueError('dim must be either -1 (nether), 0 (overworld), or 1 (end)')
        self.dim = dim

    def nether(self):
        if self.dim == 0:
            return Coord(math.floor(self.x / 8), math.floor(self.z / 8), dim=-1)
        else:
            return self

    def overworld(self):
        if self.dim == -1:
            return Coord(int(self.x * 8), int(self.z * 8))
        else:
            return self

    def info(self):
        if self.y:
            y = self.y
        else:
            y = '~'
        if self.dim == 0:
            print(f'Located at ({self.x}, {y}, {self.z}) in the Overworld.')
            print(f'Corresponds to ({self.nether().x}, ~, {self.nether().z}) in the Nether.')
        elif self.dim == -1:
            print(f'Located at ({self.x}, {y}, {self.z}) in the Nether.')
            print(f'Corresponds to ({self.overworld().x}, ~, {self.overworld().z}) in the Overworld.')
        elif self.dim == 1:
            print(f'Located at ({self.x}, {y}, {self.z}) in the End.')


def taxi(a: Coord, b: Coord):
    if a.dim != b.dim:
        raise ValueError('Taxicab distance calculation requires both coordinates to be in the same dimension!')
    if a.y is None or b.y is None:
        return abs(a.x - b.x) + abs(a.z - b.z)
    else:
        return abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z)


def dist(a: Coord, b: Coord):
    if a.dim != b.dim:
        raise ValueError('Distance calculation requires both coordinates to be in the same dimension!')
    if a.y is None or b.y is None:
        return math.sqrt((a.x - b.x) ** 2 + (a.z - b.z) ** 2)
    else:
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def time(distance: float, speed: float):
    return distance * speed ** -1


def travel(from_: Coord, to_: Coord):
    if from_.dim != to_.dim:
        raise ValueError('Distance calculation requires both coordinates to be in the same dimension!')
    x_diff = to_.x - from_.x
    z_diff = to_.z - from_.z

    if x_diff >= 0:
        direction_x = 'East'
    else:
        direction_x = 'West'

    if z_diff >= 0:
        direction_z = 'South'
    else:
        direction_z = 'North'

    # direction = math.degrees(math.atan2(-x_diff, z_diff)) TODO
    # if z_diff > 0 and x_diff < 0:
    #     dir_vector = direction
    #     print('h')
    # elif z_diff > 0 and x_diff > 0:
    #     dir_vector = -direction
    #     print('j')
    # elif z_diff < 0 and x_diff < 0:
    #     dir_vector = 180 - direction
    #     print('k')
    # elif z_diff < 0 and x_diff > 0:
    #     dir_vector = -(180 - direction)
    #     print('l')
    # else:
    #     dir_vector = direction
    #     print('wtf')

    print(f'From ({from_.x}, {from_.z}) towards ({to_.x}, {to_.z}), you must travel {abs(int(x_diff))} blocks {direction_x} and {abs(int(z_diff))} blocks {direction_z}.')
    # print(f'Exact angle is {dir_vector:.1f}°.')
