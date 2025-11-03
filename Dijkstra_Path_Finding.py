import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dijkstra's Path Finding Algorithm")

# --- Color Definitions ---
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0) # Note: BLUE was same as GREEN in your code, kept it
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    # --- State checking methods ---
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    # --- State setting methods ---
    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        """ Populates self.neighbors with valid (non-barrier) neighbors """
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        """ Allows comparison for PriorityQueue """
        return False

# Heuristic function (h) is NOT needed for Dijkstra's


def reconstruct_path(came_from, current, draw):
    """ Draws the final path by backtracking from the end node """
    while current in came_from:
        current = came_from[current]
        if not current.is_start(): # Avoid overwriting start color
            current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    """
    Performs Dijkstra's algorithm.
    Prioritizes nodes based on g_score (distance from start) only.
    """
    count = 0
    open_set = PriorityQueue()
    # Priority is g_score, count (tie-breaker), node
    open_set.put((0, count, start))
    
    came_from = {}
    
    # g_score: Cost from start to this node
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    
    # f_score is removed (not used in Dijkstra's)
    
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False # Exit if window is closed

        current = open_set.get()[2] # Get the node with the smallest g_score
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end() # Ensure end node stays its color
            start.make_start() # Ensure start node stays its color
            return True # Path found

        for neighbor in current.neighbors:
            # Assumes cost from current to neighbor is 1
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                # This is a better path to the neighbor
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                
                if neighbor not in open_set_hash:
                    count += 1
                    # Add to queue using g_score as priority
                    open_set.put((g_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open() # Mark as "to be visited"

        draw()

        if current != start:
            current.make_closed() # Mark as "visited"

    return False # Path not found


def make_grid(rows, width):
    """ Creates the 2D grid of Spot objects """
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid


def draw_grid_lines(win, rows, width):
    """ Draws the grid lines on the window """
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for j in range(rows):
        pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    """ Main drawing function, called every frame """
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win) # Draw each spot

    draw_grid_lines(win, rows, width) # Draw grid lines over spots
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    """ Converts pixel coordinates (x, y) to grid coordinates (row, col) """
    gap = width // rows
    x, y = pos

    col = x // gap
    row = y // gap

    # Clamp to grid bounds (handles clicks on the very edge)
    if row >= rows:
        row = rows - 1
    if col >= rows:
        col = rows - 1
        
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False # Flag to check if algorithm is running

    while run:
        draw(win, grid, ROWS, width)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Don't allow clicking if algorithm is running
            if started:
                continue

            # LEFT MOUSE BUTTON
            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            # RIGHT MOUSE BUTTON
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # KEY PRESSES
            if event.type == pygame.KEYDOWN:
                # Start algorithm
                if event.key == pygame.K_SPACE and start and end and not started:
                    started = True
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    started = False # Algorithm finished

                # Clear grid
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    started = False
                    grid = make_grid(ROWS, width)

    pygame.quit()

# --- Initialize Pygame and run the main function ---
if __name__ == "__main__":
    pygame.init() # Initialize pygame modules
    main(WIN, WIDTH)
