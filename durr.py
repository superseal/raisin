# from __future__ import print_function
from random import randrange, randint, sample, uniform
from utils import flatten, say, sprunge
from threading import Timer

class Cell():
    def __init__(self, biome):
        self.wood = randint(0, 1)
        self.stone = randint(0, 1)
        self.iron = randint(0, 1)
        self.food = randint(0, 1)
        self.owner = 'nature'
        self.town = None
        # Cell type: mountain, lake, forest, etc
        self.biome = biome
        if biome is 'mountain':
            self.wood += 2 + randint(0, 3)
            self.stone += 5 + randint(0, 3)
            self.iron += 4 + randint(0, 2)
            self.food += 1 + randint(0, 1)
        elif biome is 'lake':
            self.food += 3 + randint(0, 3)
        elif biome is 'forest':
            self.wood += 5 + randint(0, 3)
            self.food += 3 + randint(0, 2)
        elif biome is 'plains':
            pass

    def __str__(self):
        biome = self.biome
        if biome is 'mountain':
            return '/\\'
        elif biome is 'lake':
            return '~~'
        elif biome is 'forest':
            return '**'
        elif biome is 'plains':
            return '..'
        elif biome is 'town':
            return '##'

class World():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        default_cell = Cell('plains')
        self.grid = [[default_cell for i in xrange(0, width)] for i in xrange(0, height)]
        # Visible portions of world
        # corners = [(0, 10), (600, 600)] # Hide first 10 rows of a 600x600 world
        self.world_corners = [(0, 0), (width - 1, height - 1)]
        # Number of cells to extend from viewfinder focus
        # extensions = [5, 3] # Creates a viewfinder of size (5*2 + 1) x (3*2 + 1)
        self.populate_grid()

    def random_coords(self):
        corners = self.world_corners
        lower_col, upper_col, lower_row, upper_row = corners[0][0], corners[1][0], corners[0][1], corners[1][1]
        return [randrange(lower_row, upper_row), randrange(lower_col, upper_col)]

    def boundary(self, position):
        y, x = position[0], position[1]
        cell_list = [(row, col) 
                for col in range(x - 1, x + 2) if col >= 0 and col < self.width 
                for row in range(y - 1, y + 2) if row >= 0 and row < self.height]
        cell_list.remove((y, x))
        return cell_list
    
    @staticmethod 
    def sample_size(boundary):
        return int(len(boundary) * uniform(0.20, 0.65))

    def random_cells(self, initial_center, iterations):
        # Cells being searched for boundaries 
        centers = [initial_center]
        # Boundaries of cells
        bounds = [self.boundary(initial_center) for center in centers]
        # Random generated cells so far
        generated_cells = []
        # Don't go over maximum distance from initial center
        for i in xrange(0, iterations):
            # Analyze all centers
            for center in centers:
                # Full boundary of cell
                center_boundary = self.boundary(center)
                # Sample boundary of same cell
                sample_boundary = sample(center_boundary, self.sample_size(center_boundary))
                for cell in sample_boundary:
                    generated_cells.append((cell[0], cell[1]))
                # New boundary are now the cells to be searched
                centers = sample_boundary
        generated_cells.append(initial_center)
        return generated_cells

    def random_generation(self, cores, max_iterations, cell_type):
        for m in xrange(0, cores):
            center = self.random_coords()
            generated_cells = self.random_cells(center, max_iterations)
            for cell in generated_cells:
                row, col = cell[0], cell[1]
                self.grid[row][col] = Cell(cell_type)

    def populate_grid(self):
        self.random_generation(self.width * self.height / 200, 2, 'mountain')
        self.random_generation(self.width * self.height / 150, 3, 'lake')
        self.random_generation(self.width * self.height / 80, 7, 'forest')
        self.random_generation(self.width * self.height / 100, 4, 'plains')

    @staticmethod
    def viewfinder_corners(corners, position, extensions):
        # [(1, 2), (10, 20)] -> [-1, 10, -2, 20]
        corners = [-corners[0][0], corners[1][0], -corners[0][1], corners[1][1]]
        # [5, 4] -> [5, 5, 4, 4]
        extensions = flatten([(x, x) for x in extensions])
        # [2, 3] -> [-2, 2, -3, 3]
        position = flatten([(-x, x) for x in position])
        visible = []
        for corner, extension, coordinate in zip(corners, extensions, position):
            extended_coordinate = coordinate + extension
            if extended_coordinate < corner:
                visible.append(abs(extended_coordinate))
            else:
                visible.append(abs(corner))
        return visible

    def viewfinder(self, position, extensions):
        corners = self.viewfinder_corners(self.world_corners, position, extensions)
        lower_row, upper_row, lower_col, upper_col = corners[0], corners[1], corners[2], corners[3]
        viewfinder = ''
        viewfinder += 'Centered at [%s, %s]\n\n' % (position[0], position[1])
        # Column labels
        viewfinder += '   '
        for col in xrange(lower_col, upper_col + 1):
            viewfinder += '%02d ' % (col % 100)
        viewfinder += '\n'
        # World
        for row in xrange(lower_row, upper_row + 1):
            viewfinder += '%02d ' % (row % 100)
            for col in xrange(lower_col, upper_col + 1):
                if row == position[0] and col == position[1]:
                    viewfinder += str(self.grid[row][col]) + '@'
                else:
                    viewfinder += str(self.grid[row][col]) + ' '
            viewfinder += '%02d ' % (row % 100)
            viewfinder += '\n'
        # Second column labels
        viewfinder += '   '
        for col in xrange(lower_col, upper_col + 1):
            viewfinder += '%02d ' % (col % 100)
        return viewfinder

class Town(Cell):
    def __init__(self, name, owner):
        Cell.__init__(self, 'town')
        self.name = name
        self.owner = owner
        # [wood, stone, iron, food]
        self.resources = [0, 0, 0, 0]
        self.buildings = []

class Workers():
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.position = [-1, -1]
        self.skills = 1
        self.resources = [0, 0, 0, 0]

class Troop():
    def __init__(self, name, position, infantry, advanced_infantry, artillery, advanced_artillery):
        self.name = name
        self.position = position
        self.infantry = infantry
        self.advanced_infantry = advanced_infantry
        self.artillery = artillery
        self.advanced_artillery = advanced_artillery

class Player():
    def __init__(self, name):
        self.name = name
        self.towns = []
        self.capital = None
        self.troops = []
        self.troop_gear = []
        self.workers = []
        # First batch of workers
        first_workers = Workers('first', 10)
        first_workers.resources = [1000, 1000, 1000, 1000]
        self.workers.append(first_workers)

class Game(object):
    def __init__(self):
        self.players = []
        self.world = World(100, 100)

    # Synergic integration that boosts the productivity of your cloud-enabled business
    def get_player(self, player_name):
        for player in self.players:
            if player.name == player_name:
                return player

    def get_troop(self, player, troop_name):
        for troop in player.troops:
            if troop.name == troop_name:
                return troop

    def get_speed(self, troop):
        return 1
                
    def join_game(self, player_name):
        if player_name not in self.players:
            new_player = Player(player_name)
            new_player.workers[0].position = self.world.random_coords()
            self.players.append(new_player)
            say(player_name, '%s: now playing' % player_name)
        else:
            say(player_name, '%s: already playing' % player_name)
    
    def viewfinder(self, player):
        center = [0, 0]
        if player.capital:
            center = player.capital.position
        elif player.workers[0]:
            center = player.workers[0].position
        return self.world.viewfinder(center, [10, 10])

    def panel(self, player_name):
        player = self.get_player(player_name)
        panel = ''
        panel += '=== Towns ===\n'
        if not player.towns:
            panel += ' (none yet)\n'
        else:
            for town in player.towns:
                panel += ' * %s:' % town.name
                panel += ' %s wood,' % town.resources[0]
                panel += ' %s stone,' % town.resources[1]
                panel += ' %s iron,' % town.resources[2]
                panel += ' %s food\n' % town.resources[3]
        panel += '\n'

        panel += '=== Workers ===\n'
        if not player.workers:
            panel += ' (no workers)\n'
        else:
            for group in player.workers:
                panel += ' * %s: ' % group.name
                panel += ' %s workers,' % group.number
                panel += ' %s,' % group.position
                panel += ' level %s\n' % group.skills
        panel += '\n'
        
        panel += '=== Troops ===\n'
        if not player.troops:
            panel += ' (no troops)\n'
        else:
            for troop in player.troops:
                panel += ' * %s: ' % troop.name
                panel += ' %s units of infantry,' % troop.infantry
                panel += ' %s units of advanced infantry,' % troop.advanced_infantry
                panel += ' %s units of artillery,' % troop.artillery
                panel += ' %s units of advanced artillery,' % troop.advanced_artillery
        panel += '\n'

        panel += self.viewfinder(player)
        return panel
        
    def settle(self, player_name, group_name):
        player = self.get_player(player_name)
        # Enough resources
        if group.resources > [1000, 1000, 1000, 1000]:
            group.resources = [resource - 1000 for resource in group.resources]
            self.world.grid[group.position[0]][group.position[1]] = Town(player.name)
            say(player, 'You have settled in position %s.' % group.position)
        else:
            say(player, 'Could not settle in position %s. Make sure your worker group'
                   ' has enough resources.' % group.position)

    # Currently using distance/speed, switch later to straight line interpolation
    def move(self, player_name, troop_name, new_position):
        player = self.get_player(player_name)
        troop = self.get_troop(troop_name)
        troop_speed = get_speed(troop)
        position = troop.position
        distance = sqrt((new_position[0] - position[0]) ** 2 + (new_position[1] - position[1]) ** 2)
        time = distance/troop_speed
        def finish_movement():
            troop.position = new_position
            say(player_name, "The troop %s is now at position %s." % (troop_name, new_position))
        timer = threading.Timer(time, finish_movement).start()
        
game = Game()
print game.world.viewfinder([25, 25], [500, 500])
# print sprunge(game.world.viewfinder([10, 10], [500, 500]))
