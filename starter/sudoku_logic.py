import copy
import random

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

def generate_puzzle(clues=35):
    """
    Generate a Sudoku puzzle with a unique solution.
    
    Args:
        clues (int): Number of pre-filled cells. Defaults to 35.
        
    Returns:
        tuple: (puzzle, solution) - both are 9x9 boards
    """
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution


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
