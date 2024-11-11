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

# Read the Sudoku grid
grid = read_grid()

# Solve the Sudoku puzzle
if solve(grid):
    print(f'\n\nSolved Sudoku puzzle:')
    print_grid(grid)
else:
    print('No solution exists!')

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

# Solve the Sudoku puzzle with Forward Checking
if solve_fc(grid, domains):
    print(f'\n\nSolved Sudoku puzzle with Forward Checking:')
    print_grid(grid)
else:
    print("No solution exists")


