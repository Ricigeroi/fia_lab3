import random


def read_grid():
    grid = []
    for _ in range(9):
        line = input()
        # Remove any leading or trailing whitespaces
        line = line.strip()
        # Pad the line to 9 characters, adding '*' at the beginning
        line = line.rjust(9, '*')
        row = []
        for c in line:
            if c == '*':
                row.append(0)
            else:
                row.append(int(c))
        grid.append(row)
    return grid

def print_grid(grid):
    for row in grid:
        print(''.join(str(num) for num in row))

def find_empty(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j  # row, col
    return None

def is_valid(grid, num, pos):
    row, col = pos
    # Check row
    for j in range(9):
        if grid[row][j] == num and j != col:
            return False
    # Check column
    for i in range(9):
        if grid[i][col] == num and i != row:
            return False
    # Check box
    box_x = col // 3
    box_y = row // 3
    for i in range(box_y * 3, box_y * 3 +3):
        for j in range(box_x *3, box_x *3 +3):
            if grid[i][j] == num and (i,j) != pos:
                return False
    return True

def solve(grid):
    find = find_empty(grid)
    if not find:
        return True  # Solved
    else:
        row, col = find
    for num in range(1,10):
        if is_valid(grid, num, (row, col)):
            grid[row][col] = num
            if solve(grid):
                return True
            grid[row][col] = 0
    return False

def generate_full_grid():
    grid = [[0]*9 for _ in range(9)]
    numbers = list(range(1, 10))

    def fill_grid(grid):
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(grid, num, (i, j)):
                            grid[i][j] = num
                            if not find_empty(grid) or fill_grid(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True

    fill_grid(grid)
    return grid

def remove_numbers(grid, holes=40):
    grid_copy = [row[:] for row in grid]
    count = 0
    while count < holes:
        i = random.randint(0, 8)
        j = random.randint(0, 8)
        if grid_copy[i][j] != 0:
            grid_copy[i][j] = 0
            count += 1
    return grid_copy

# Generate a full valid Sudoku grid
full_grid = generate_full_grid()

# Remove numbers to create a puzzle
puzzle_grid = remove_numbers(full_grid, holes=40)

# Read the Sudoku grid
print("\nGenerated Sudoku puzzle:")
print_grid(puzzle_grid)
#grid = read_grid()
grid = puzzle_grid


# Task 2: Constraint Propagation

def initialize_domains(grid):
    domains = [[set(range(1,10)) for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                domains[i][j] = set([grid[i][j]])
    return domains

def propagate_constraints(domains):
    changed = True
    while changed:
        changed = False
        for i in range(9):
            for j in range(9):
                if len(domains[i][j]) == 1:
                    value = next(iter(domains[i][j]))
                    # Remove this value from peers
                    # Row
                    for col in range(9):
                        if col != j and value in domains[i][col]:
                            domains[i][col].remove(value)
                            changed = True
                    # Column
                    for row in range(9):
                        if row != i and value in domains[row][j]:
                            domains[row][j].remove(value)
                            changed = True
                    # Box
                    box_row = i //3
                    box_col = j //3
                    for row in range(box_row*3, box_row*3+3):
                        for col in range(box_col*3, box_col*3+3):
                            if (row != i or col != j) and value in domains[row][col]:
                                domains[row][col].remove(value)
                                changed = True
    return domains

# Initialize domains and propagate constraints
domains = initialize_domains(grid)
domains = propagate_constraints(domains)

# Task 3: Backtracking with Forward Checking

def solve_fc(grid, domains):
    # Find the unassigned cell with the smallest domain
    min_domain_size = 10
    cell = None
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                domain_size = len(domains[i][j])
                if domain_size == 0:
                    return False  # No possible values, backtrack
                if domain_size < min_domain_size:
                    min_domain_size = domain_size
                    cell = (i, j)
    if cell is None:
        return True  # Solved
    row, col = cell
    for value in domains[row][col]:
        # Create copies of grid and domains
        grid_copy = [row[:] for row in grid]
        domains_copy = [ [domains[i][j].copy() for j in range(9)] for i in range(9)]
        grid_copy[row][col] = value
        domains_copy[row][col] = set([value])
        # Forward checking
        forward_checking = True
        # Row
        for col2 in range(9):
            if col2 != col and value in domains_copy[row][col2]:
                domains_copy[row][col2].remove(value)
                if len(domains_copy[row][col2]) == 0:
                    forward_checking = False
                    break
        if not forward_checking:
            continue
        # Column
        for row2 in range(9):
            if row2 != row and value in domains_copy[row2][col]:
                domains_copy[row2][col].remove(value)
                if len(domains_copy[row2][col]) == 0:
                    forward_checking = False
                    break
        if not forward_checking:
            continue
        # Box
        box_row = row //3
        box_col = col //3
        for i in range(box_row*3, box_row*3+3):
            for j in range(box_col*3, box_col*3+3):
                if (i != row or j != col) and value in domains_copy[i][j]:
                    domains_copy[i][j].remove(value)
                    if len(domains_copy[i][j]) == 0:
                        forward_checking = False
                        break
            if not forward_checking:
                break
        if not forward_checking:
            continue
        # Propagate constraints
        domains_copy = propagate_constraints(domains_copy)
        # Recursive call
        if solve_fc(grid_copy, domains_copy):
            # Update the original grid
            for i in range(9):
                grid[i] = grid_copy[i]
            return True
    return False



# Your heuristic solver code

def get_units():
    units = []
    # Rows
    for i in range(9):
        units.append([(i, j) for j in range(9)])
    # Columns
    for j in range(9):
        units.append([(i, j) for i in range(9)])
    # Boxes
    for box_row in range(3):
        for box_col in range(3):
            unit = []
            for i in range(box_row * 3, box_row * 3 + 3):
                for j in range(box_col * 3, box_col * 3 + 3):
                    unit.append((i, j))
            units.append(unit)
    return units

def solve_heuristic(grid, domains):
    progress = True
    while progress:
        progress = False
        # Naked Singles
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0 and len(domains[i][j]) == 1:
                    value = next(iter(domains[i][j]))
                    grid[i][j] = value
                    domains[i][j] = set([value])
                    # Remove value from peers
                    # Row
                    for col in range(9):
                        if col != j and value in domains[i][col]:
                            domains[i][col].remove(value)
                            progress = True
                    # Column
                    for row in range(9):
                        if row != i and value in domains[row][j]:
                            domains[row][j].remove(value)
                            progress = True
                    # Box
                    box_row = i // 3
                    box_col = j // 3
                    for row in range(box_row * 3, box_row * 3 + 3):
                        for col in range(box_col * 3, box_col * 3 + 3):
                            if (row != i or col != j) and value in domains[row][col]:
                                domains[row][col].remove(value)
                                progress = True
        # Hidden Singles
        for unit in get_units():
            counts = {}
            for (i, j) in unit:
                if grid[i][j] == 0:
                    for value in domains[i][j]:
                        counts.setdefault(value, []).append((i, j))
            for value, positions in counts.items():
                if len(positions) == 1:
                    i, j = positions[0]
                    if grid[i][j] == 0:
                        grid[i][j] = value
                        domains[i][j] = set([value])
                        # Remove value from peers
                        # Row
                        for col in range(9):
                            if col != j and value in domains[i][col]:
                                domains[i][col].remove(value)
                                progress = True
                        # Column
                        for row in range(9):
                            if row != i and value in domains[row][j]:
                                domains[row][j].remove(value)
                                progress = True
                        # Box
                        box_row = i // 3
                        box_col = j // 3
                        for row in range(box_row * 3, box_row * 3 + 3):
                            for col in range(box_col * 3, box_col * 3 + 3):
                                if (row != i or col != j) and value in domains[row][col]:
                                    domains[row][col].remove(value)
                                    progress = True
        # Check if grid is complete
        if all(grid[i][j] != 0 for i in range(9) for j in range(9)):
            return True  # Solved
    return False  # No further progress can be made

# Initialize domains and propagate constraints
domains = initialize_domains(grid)
domains = propagate_constraints(domains)


backtracking_solution = solve(grid)
if backtracking_solution:
    print(f'\n\nSolved Sudoku puzzle with backtracking:')
    print_grid(grid)
else:
    print('No solution exists!')

forward_checking_solution = solve_fc(grid, domains)
if forward_checking_solution:
    print(f'\n\nSolved Sudoku puzzle with Forward Checking:')
    print_grid(grid)
else:
    print("No solution exists")

heuristic_solution = solve_heuristic(grid, domains)
if heuristic_solution:
    print(f'\n\nSolved Sudoku puzzle with Heuristic Algorithm:')
    print_grid(grid)
else:
    print("No solution exists using heuristic method")

# test all three solutions
assert backtracking_solution == forward_checking_solution == heuristic_solution