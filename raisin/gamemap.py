import itertools
import random

width, height = 40, 40
byteboard = bytearray(width * height * 2)

def position(row, col):
    global width, height
    # Wrap around world edges
    row, col = row % height, col % width
    return 2 * ((width * row) + col)

def board(row, col):
    global width, height, byteboard
    pos = position(row, col)
    return byteboard[pos:pos + 2]

def board_set(row, col, tile):
    global width, height, byteboard
    assert len(tile) == 2
    pos = position(row, col)
    byteboard[pos], byteboard[pos + 1] = tile[0], tile[1]

def board_print():
    global width, height, byteboard
    pos = 0
    # No spaces between cells
    for row in range(height):
        print ''.join(str(byteboard[2 * row * width:2 * (row + 1) * width]))
    # Spaces between cells
    """
    for row in range(height):
        for col in range(width):
            print board(row, col),
        print
    """

def bisec(x, y, depth=0):
    if depth >= 2:
        return []
    else:
        mid = (x + y) / 2.0
        #offset = random.uniform(0, mid / 8)
        #mid += offset
        return bisec(x, mid, depth + 1) + [mid] + bisec(mid, y, depth + 1)


# Get all cells in a radius of (size) cells
def neighborhood(row, col, rad):
    return [(r, c) for r, c in itertools.product(
            range(row - rad, row + rad + 1), 
            range(col - rad, col + rad + 1)) if (row - r)**2 + (col - c)**2 <= rad**2]

def boundary(neighborhood):
    return [(r, c) for r, c in neighborhood if '..' in 
            (board(r + 1, c), board(r, c + 1), board(r - 1, c), board(r, c - 1))]

# Get immediate neighbors
def one_away(row, col):
    one = [c for c in neighborhood(row, col, 2)]
    for c in ((row, col), (row + 2, col), (row, col + 2), (row - 2, col), (row, col - 2)):
        one.remove(c)
    return one

def make_blob(row, col, tile, min_rad, max_rad):
    # Populate cells within (min_rad) units right away
    n = neighborhood(row, col, min_rad)
    for a, b in n:
        board_set(a, b, tile)

    # Populate cells between (min_rad) and (max_rad) randomly
    frontier = set(boundary(n))
    for i in xrange(max_rad - min_rad):
        next_frontier = set()
        for (r, c) in frontier:
            one = one_away(r, c)
            sample_size = int(8 * random.uniform(0, 0.7))
            frontier_sample = random.sample(one, sample_size)
            for sr, sc in frontier_sample:
                board_set(sr, sc, tile)
                next_frontier.add((sr, sc))
        frontier = next_frontier

def viewfinder(row, col, h_size, v_size):
    global byteboard, width, height
    left_col = col - h_size
    right_col = col + h_size
    top_row = row - v_size
    bottom_row = row + v_size

    column_labels = ["## "] + ["%02d " % ((c % width) % 100) for c in range(left_col, right_col + 1)] + ["##\n"]
    rows = []
    for r in range(top_row, bottom_row + 1):
        new_row = ["%02d " % ((r % height) % 100)]
        for c in range(left_col, bottom_row + 1):
            if r == row and (c == col or c == col - 1):
                new_row.append(str((board(r, c))) + '@')
            else:
                new_row.append(str((board(r, c))) + ' ')
        new_row.append("%02d\n" % ((r % height) % 100))
        rows.extend(new_row)
    return ''.join(column_labels + rows + column_labels)

########################

for row in range(height):
    for col in range(width):
        board_set(row, col, '..')

rand_coords = [(random.randrange(0, height), random.randrange(0, width)) for _ in xrange(0, 5)]
for row, col in rand_coords:
    min_rad = random.randrange(3, 5)
    max_rad = min_rad + random.randrange(1, 3)
    make_blob(row, col, "**", min_rad, max_rad)
board_print()

print viewfinder(30, 30, 30, 30)

####

players = {}

def inside(point, corners):
    l = len(corners)
    walls = [0, 0, 0, 0]
    row, col = point
    # Must have an even number of corners to be closed
    if l % 2 != 0:
        return "broken number"
    # A point cannot be inside if it's not in the square formed by min/max coords
    inf = float('inf')
    min_row, min_col, max_row, max_col = inf, inf, -inf, -inf
    for c in corners:
        if c[0] < min_row: min_row = c[0]
        if c[0] > max_row: max_row = c[0]
        if c[1] < min_col: min_col = c[1]
        if c[1] > max_col: max_col = c[1]
    if row < min_row or row > max_row or col < min_col or col > max_col:
        return "out of bounds"
    # A point is inside only if it's surrounded by walls in all directions
    for i in range(len(corners)):
        c = corners[i % l]
        n = corners[(i + 1) % l]
        # corners must be a clockwise listing
        # Every corner has at least one common coordinate with the next corner
        if c[0] != n[0] and c[1] != n[1]:
            return "broken wall"
        else:
            # Found a horizontal wall            
            min_c = min(c[1], n[1])
            max_c = max(c[1], n[1])
            if c[0] == n[0] and min_c <= col <= max_c:
                hwall = (c[0], c[0], min_c, max_c)
                if row == c[0]: return "hwall"
                elif row > c[0]: walls[0] = hwall; # North wall
                elif row < c[0]: walls[2] = hwall; # South wall
            # Found a vertical_wall
            min_r = min(c[0], n[0])
            max_r = max(c[0], n[0])
            if c[1] == n[1] and min_r <= row <= max_r:
                vwall = (min_r, max_r, c[1], c[1])
                if col == c[1]: return "vwall"
                elif col > c[1]: walls[1] = vwall; # West wall
                elif col < c[1]: walls[3] = vwall; # East wall
    if 0 in walls:
        return "outside"
    else:
        return "inside"

c = [(0, 0), (0, 9), (4, 9), (4, 6), (5, 6), (5, 11), (10, 11), (10, 7), (9, 7), (9, 5), (11, 5), (11, 1), (6, 1), (6, 3), (3, 3), (3, 0)]
d = [(1, 1), (1, 4), (0, 4), (0, 6), (3, 6), (3, 11), (7, 11), (7, 9), (5, 9), (5, 7), (9, 7), (9, 10), (16, 10), (16, 7), (13, 7), (13, 6), (11, 6), (11, 4), (13, 4), (13, 3), (16, 3), (16, 0), (8, 0), (8, 2), (7, 2), (7, 4), (3, 4), (3, 3), (5, 3), (5, 1)]

width, height = 20, 20
a = [["--" for _ in range(width)] for _ in range(height)] 
for row in range(height):
    for col in range(width):
        status = inside((row, col), c) 
        if status == 'outside':
            a[row][col] = '..'
        elif status == 'inside':
            a[row][col] = '::'
        elif status == 'hwall' or status == 'vwall':
            a[row][col] = '##'

for row in a:
    print ''.join(row)
