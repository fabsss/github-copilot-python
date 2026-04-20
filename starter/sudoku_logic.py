import copy
import random
import time

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def count_solutions(board, limit=2):
    """
    Count the number of solutions for a Sudoku puzzle.
    
    Args:
        board (list): 9x9 Sudoku board with 0s for empty cells
        limit (int): Stop counting after reaching this limit (for efficiency)
        
    Returns:
        int: Number of solutions found (up to limit)
    """
    if not board or len(board) != SIZE or not all(len(row) == SIZE for row in board):
        return 0
    
    board_copy = deep_copy(board)
    count = [0]  # Use list to allow modification in nested function
    
    def backtrack():
        if count[0] >= limit:
            return  # Stop if we've found enough solutions
        
        for row in range(SIZE):
            for col in range(SIZE):
                if board_copy[row][col] == EMPTY:
                    for num in range(1, SIZE + 1):
                        if is_safe(board_copy, row, col, num):
                            board_copy[row][col] = num
                            backtrack()
                            board_copy[row][col] = EMPTY
                    return
        count[0] += 1
    
    backtrack()
    return count[0]


def has_unique_solution(puzzle):
    """
    Check if a puzzle has exactly one unique solution.
    
    Args:
        puzzle (list): 9x9 Sudoku puzzle with 0s for empty cells
        
    Returns:
        bool: True if puzzle has exactly one solution, False otherwise
    """
    return count_solutions(puzzle, limit=2) == 1


def generate_puzzle(clues=35, max_attempts=100, timeout_seconds=5):
    """
    Generate a Sudoku puzzle with guaranteed unique solution.
    
    Args:
        clues (int): Target number of pre-filled cells. Defaults to 35.
        max_attempts (int): Maximum attempts to generate a valid puzzle. Defaults to 100.
        timeout_seconds (int): Maximum time in seconds to generate a puzzle. Defaults to 5.
        
    Returns:
        tuple: (puzzle, solution) - both are 9x9 boards, puzzle guaranteed to have unique solution
        
    Raises:
        TimeoutError: If unable to generate a puzzle with unique solution within timeout_seconds
    """
    start_time = time.time()
    
    def time_remaining():
        elapsed = time.time() - start_time
        return timeout_seconds - elapsed
    
    for attempt in range(max_attempts):
        if time_remaining() <= 0:
            raise TimeoutError(
                f"Could not generate a puzzle with unique solution within {timeout_seconds} seconds. "
                "Please try again by clicking 'New Game'."
            )
        
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        
        # Remove cells one by one, maintaining a solvable puzzle with unique solution
        cells_to_remove = SIZE * SIZE - clues
        removed = 0
        attempts = 0
        max_remove_attempts = SIZE * SIZE * 2
        
        while removed < cells_to_remove and attempts < max_remove_attempts:
            if time_remaining() <= 0:
                raise TimeoutError(
                    f"Could not generate a puzzle with unique solution within {timeout_seconds} seconds. "
                    "Please try again by clicking 'New Game'."
                )
            
            row = random.randrange(SIZE)
            col = random.randrange(SIZE)
            attempts += 1
            
            if board[row][col] != EMPTY:
                # Try removing this cell
                value = board[row][col]
                board[row][col] = EMPTY
                
                # Check if puzzle still has unique solution
                if has_unique_solution(board):
                    removed += 1
                    attempts = 0  # Reset attempts counter on successful removal
                else:
                    # Put the value back if it violates uniqueness
                    board[row][col] = value
        
        # If we successfully removed enough cells, return the puzzle
        if removed >= clues * 0.9:  # Allow 90% of target clues
            puzzle = deep_copy(board)
            return puzzle, solution
    
    # Fallback: guarantee uniqueness with timeout
    # Keep generating and validating until we get a unique solution or timeout
    while time_remaining() > 0:
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        remove_cells(board, clues)
        puzzle = deep_copy(board)
        
        # MUST validate uniqueness - never skip this
        if has_unique_solution(puzzle):
            return puzzle, solution
        
        # If not unique, try again (loop will continue or timeout)
    
    # Timeout exceeded - raise error
    raise TimeoutError(
        f"Could not generate a puzzle with unique solution within {timeout_seconds} seconds. "
        "Please try again by clicking 'New Game'."
    )


def is_valid_move(num, row, col, board=None):
    """
    Check if placing a number at a position is a valid move.
    
    Args:
        num (int): Number to place (1-9)
        row (int): Row index (0-8)
        col (int): Column index (0-8)
        board (list): Optional board state. If None, assumes placement is theoretically valid.
        
    Returns:
        bool: True if the move is valid, False otherwise
    """
    if not isinstance(num, int) or num < 1 or num > SIZE:
        return False
    if not (0 <= row < SIZE and 0 <= col < SIZE):
        return False
    if board is None:
        return True
    return is_safe(board, row, col, num)


def solve_sudoku(board):
    """
    Solve a Sudoku puzzle using backtracking.
    
    Args:
        board (list): 9x9 Sudoku board with 0s for empty cells
        
    Returns:
        bool: True if puzzle is solvable, False otherwise
    """
    if not board or len(board) != SIZE or not all(len(row) == SIZE for row in board):
        return False
    
    board_copy = deep_copy(board)
    
    def backtrack():
        for row in range(SIZE):
            for col in range(SIZE):
                if board_copy[row][col] == EMPTY:
                    for num in range(1, SIZE + 1):
                        if is_safe(board_copy, row, col, num):
                            board_copy[row][col] = num
                            if backtrack():
                                return True
                            board_copy[row][col] = EMPTY
                    return False
        return True
    
    return backtrack()


def check_sudoku_solution(board):
    """
    Check if a board is a valid and complete Sudoku solution.
    
    Args:
        board (list): 9x9 Sudoku board
        
    Returns:
        bool: True if board is a valid complete solution, False otherwise
    """
    if not board or len(board) != SIZE or not all(len(row) == SIZE for row in board):
        return False
    
    # Check all cells are filled (no zeros)
    for row in board:
        if EMPTY in row:
            return False
    
    # Check rows
    for row in board:
        if len(set(row)) != SIZE or any(num < 1 or num > SIZE for num in row):
            return False
    
    # Check columns
    for col in range(SIZE):
        column = [board[row][col] for row in range(SIZE)]
        if len(set(column)) != SIZE:
            return False
    
    # Check 3x3 boxes
    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            box = []
            for i in range(3):
                for j in range(3):
                    box.append(board[box_row + i][box_col + j])
            if len(set(box)) != SIZE:
                return False
    
    return True
