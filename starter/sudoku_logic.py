"""Sudoku game logic and puzzle generation module.

This module provides core Sudoku functionality including:
- Puzzle generation with unique solutions
- Solution validation and verification
- Backtracking solver
- Move validation
"""

from typing import List, Tuple
import copy
import random
import time

SIZE = 9
EMPTY = 0


def deep_copy(board: List[List[int]]) -> List[List[int]]:
    """Create a deep copy of a Sudoku board.
    
    Args:
        board: 9x9 Sudoku board represented as list of lists.
        
    Returns:
        A deep copy of the board with no shared references.
    """
    return copy.deepcopy(board)


def create_empty_board() -> List[List[int]]:
    """Create an empty 9x9 Sudoku board.
    
    Returns:
        A 9x9 board with all cells initialized to EMPTY (0).
    """
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if placing a number at a cell is safe.
    
    Validates that the number doesn't conflict with existing numbers in the
    same row, column, or 3x3 box.
    
    Args:
        board: 9x9 Sudoku board.
        row: Row index (0-8).
        col: Column index (0-8).
        num: Number to check (1-9).
        
    Returns:
        True if placing num at (row, col) is valid, False otherwise.
    """
    # Check row and column
    for index in range(SIZE):
        if board[row][index] == num or board[index][col] == num:
            return False
    
    # Check 3x3 box
    box_start_row = row - row % 3
    box_start_col = col - col % 3
    for row_offset in range(3):
        for col_offset in range(3):
            if board[box_start_row + row_offset][box_start_col + col_offset] == num:
                return False
    
    return True

def fill_board(board: List[List[int]]) -> bool:
    """Fill a Sudoku board using backtracking.
    
    Recursively fills empty cells with valid numbers (1-9) ensuring no conflicts
    with existing numbers in the same row, column, or 3x3 box.
    
    Args:
        board: 9x9 Sudoku board to fill.
        
    Returns:
        True if board was successfully filled, False if no valid solution exists.
    """
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                # Try each number in random order for variety
                candidates = list(range(1, SIZE + 1))
                random.shuffle(candidates)
                
                for candidate in candidates:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        
                        if fill_board(board):
                            return True
                        
                        # Backtrack if this path doesn't lead to solution
                        board[row][col] = EMPTY
                
                return False
    
    return True

def remove_cells(board: List[List[int]], clues: int) -> None:
    """Remove cells from a completed board to create a puzzle.
    
    Randomly removes numbers from the board, keeping the specified number of clues
    (prefilled cells). This is a greedy approach and doesn't guarantee a unique
    solution - use with caution and validate with has_unique_solution().
    
    Args:
        board: 9x9 completed Sudoku board to remove cells from.
        clues: Number of cells to keep (remove SIZE*SIZE - clues cells).
        
    Returns:
        None (modifies board in place).
    """
    cells_to_remove = SIZE * SIZE - clues
    attempts = cells_to_remove
    
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def count_solutions(board: List[List[int]], limit: int = 2) -> int:
    """Count the number of solutions for a Sudoku puzzle.
    
    Uses backtracking to count distinct solutions. Stops early when reaching
    the specified limit for efficiency.
    
    Args:
        board: 9x9 Sudoku puzzle with 0s for empty cells.
        limit: Maximum number of solutions to count before stopping. Defaults to 2.
        
    Returns:
        Number of solutions found (up to limit).
    """
    if not board or len(board) != SIZE or not all(len(row) == SIZE for row in board):
        return 0
    
    board_copy = deep_copy(board)
    count = [0]  # Use list to allow modification in nested function
    
    def backtrack() -> None:
        """Recursively try to find solutions."""
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


def has_unique_solution(puzzle: List[List[int]]) -> bool:
    """Check if a puzzle has exactly one unique solution.
    
    Args:
        puzzle: 9x9 Sudoku puzzle with 0s for empty cells.
        
    Returns:
        True if puzzle has exactly one solution, False otherwise.
    """
    return count_solutions(puzzle, limit=2) == 1


def generate_puzzle(clues: int = 35, max_attempts: int = 100, 
                    timeout_seconds: int = 5) -> Tuple[List[List[int]], List[List[int]]]:
    """Generate a Sudoku puzzle with guaranteed unique solution.
    
    Creates a valid Sudoku puzzle by filling a board completely, then
    strategically removing cells while ensuring the puzzle maintains
    exactly one unique solution.
    
    Args:
        clues: Target number of pre-filled cells. Defaults to 35.
               Easy: 45, Medium: 35, Hard: 25.
        max_attempts: Maximum attempts to generate a valid puzzle. Defaults to 100.
        timeout_seconds: Maximum time in seconds to generate a puzzle. Defaults to 5.
                        Hard difficulty (25 clues) uses 15 seconds. 
                        Medium-hard (≤30 clues) uses 10 seconds.
        
    Returns:
        Tuple of (puzzle, solution) - both are 9x9 boards. Puzzle guaranteed 
        to have exactly one unique solution.
        
    Raises:
        TimeoutError: If unable to generate a puzzle with unique solution 
                     within timeout_seconds.
    """
    # Increase timeout for harder difficulties (fewer clues = harder = longer generation)
    if clues <= 25:
        timeout_seconds = 40  # Hard difficulty - allow enough time for uniqueness checks
    elif clues <= 30:
        timeout_seconds = 20  # Medium-hard
    
    start_time = time.time()
    
    def time_remaining() -> float:
        """Calculate remaining time for puzzle generation."""
        elapsed = time.time() - start_time
        return timeout_seconds - elapsed
    
    for attempt in range(max_attempts):
        if time_remaining() <= 0:
            raise TimeoutError(
                f"Could not generate a puzzle with unique solution within "
                f"{timeout_seconds} seconds. Please try again by clicking 'New Game'."
            )
        
        # Generate a completely filled board
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        
        # Remove cells strategically: prioritize cells with more conflicts
        cells_to_remove = SIZE * SIZE - clues
        removed = 0
        
        # Create list of all cell positions and shuffle them
        all_cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
        random.shuffle(all_cells)
        
        # Attempt removal in strategic order
        for row, col in all_cells:
            if time_remaining() <= 0:
                raise TimeoutError(
                    f"Could not generate a puzzle with unique solution within "
                    f"{timeout_seconds} seconds. Please try again by clicking 'New Game'."
                )
            
            if removed >= cells_to_remove:
                break  # Successfully removed enough cells
            
            if board[row][col] != EMPTY:
                # Try removing this cell
                value = board[row][col]
                board[row][col] = EMPTY
                
                # Check if puzzle still has unique solution
                if has_unique_solution(board):
                    removed += 1
                else:
                    # Put the value back if it violates uniqueness
                    board[row][col] = value
        
        # Check actual clue count in the final puzzle (cells that are not EMPTY)
        actual_clues = sum(1 for row in board for cell in row if cell != EMPTY)
        
        # Accept if actual clues meet target. Hard puzzles: 80% tolerance, others: 90%
        min_clues = clues * 0.8 if clues <= 25 else clues * 0.9
        if actual_clues >= min_clues:
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
    
    # Timeout exceeded - raise error
    raise TimeoutError(
        f"Could not generate a puzzle with unique solution within "
        f"{timeout_seconds} seconds. Please try again by clicking 'New Game'."
    )


def is_valid_move(num: int, row: int, col: int, 
                  board: List[List[int]] = None) -> bool:
    """Check if placing a number at a position is a valid move.
    
    Validates that the number is in valid range (1-9) and position is within
    bounds (0-8). If a board is provided, also checks for conflicts.
    
    Args:
        num: Number to place (1-9).
        row: Row index (0-8).
        col: Column index (0-8).
        board: Optional board state. If None, assumes placement is theoretically valid.
        
    Returns:
        True if the move is valid, False otherwise.
    """
    # Validate number range
    if not isinstance(num, int) or num < 1 or num > SIZE:
        return False
    
    # Validate position bounds
    if not (0 <= row < SIZE and 0 <= col < SIZE):
        return False
    
    # If no board provided, assume move is valid (just range check)
    if board is None:
        return True
    
    # Check for conflicts on provided board
    return is_safe(board, row, col, num)


def solve_sudoku(board: List[List[int]]) -> bool:
    """Solve a Sudoku puzzle using backtracking.
    
    Attempts to solve the given puzzle by filling empty cells with valid values
    using a backtracking algorithm.
    
    Args:
        board: 9x9 Sudoku board with 0s for empty cells.
        
    Returns:
        True if puzzle is solvable, False if input is invalid or unsolvable.
    """
    # Validate input
    if not board or len(board) != SIZE or not all(len(row) == SIZE for row in board):
        return False
    
    board_copy = deep_copy(board)
    
    def backtrack() -> bool:
        """Recursively try to solve the puzzle."""
        for row in range(SIZE):
            for col in range(SIZE):
                if board_copy[row][col] == EMPTY:
                    # Try each number 1-9
                    for num in range(1, SIZE + 1):
                        if is_safe(board_copy, row, col, num):
                            board_copy[row][col] = num
                            
                            if backtrack():
                                return True
                            
                            # Backtrack if this path doesn't lead to solution
                            board_copy[row][col] = EMPTY
                    
                    return False
        
        return True  # All cells filled successfully
    
    return backtrack()


def check_sudoku_solution(board: List[List[int]]) -> bool:
    """Check if a board is a valid and complete Sudoku solution.
    
    Validates that:
    - All cells are filled (no empty cells)
    - All rows contain digits 1-9 exactly once
    - All columns contain digits 1-9 exactly once
    - All 3x3 boxes contain digits 1-9 exactly once
    
    Args:
        board: 9x9 Sudoku board.
        
    Returns:
        True if board is a valid complete solution, False otherwise.
    """
    # Validate input
    if not board or len(board) != SIZE or not all(len(row) == SIZE for row in board):
        return False
    
    # Check all cells are filled (no zeros)
    for row in board:
        if EMPTY in row:
            return False
    
    # Check rows: each must have digits 1-9 exactly once
    for row in board:
        if len(set(row)) != SIZE or any(num < 1 or num > SIZE for num in row):
            return False
    
    # Check columns: each must have digits 1-9 exactly once
    for col_idx in range(SIZE):
        column = [board[row_idx][col_idx] for row_idx in range(SIZE)]
        if len(set(column)) != SIZE:
            return False
    
    # Check 3x3 boxes: each must have digits 1-9 exactly once
    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            box = []
            for row_offset in range(3):
                for col_offset in range(3):
                    box.append(board[box_row + row_offset][box_col + col_offset])
            
            if len(set(box)) != SIZE:
                return False
    
    return True
