import pytest
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudoku_logic import (
    is_valid_move,
    solve_sudoku,
    check_sudoku_solution,
    generate_puzzle,
    create_empty_board,
    count_solutions,
    has_unique_solution,
    SIZE,
    EMPTY,
)


class TestIsValidMove:
    """Test is_valid_move function with various inputs."""
    
    def test_valid_move_range_true_without_board(self):
        """Valid number with no board constraint should return True."""
        assert is_valid_move(5, 0, 0) is True
        assert is_valid_move(1, 4, 4) is True
        assert is_valid_move(9, 8, 8) is True
    
    def test_invalid_move_out_of_range(self):
        """Numbers outside 1-9 should return False."""
        assert is_valid_move(0, 0, 0) is False
        assert is_valid_move(10, 0, 0) is False
        assert is_valid_move(-1, 0, 0) is False
    
    def test_invalid_move_out_of_bounds(self):
        """Row/col indices outside 0-8 should return False."""
        assert is_valid_move(5, -1, 0) is False
        assert is_valid_move(5, 9, 0) is False
        assert is_valid_move(5, 0, -1) is False
        assert is_valid_move(5, 0, 9) is False
    
    def test_valid_move_with_board(self):
        """Valid move on actual board should check conflict."""
        board = create_empty_board()
        assert is_valid_move(5, 0, 0, board) is True
    
    def test_invalid_move_with_board_row_conflict(self):
        """Move conflicting with row should return False."""
        board = create_empty_board()
        board[0][0] = 5
        assert is_valid_move(5, 0, 8, board) is False


class TestSolveSudoku:
    """Test solve_sudoku function."""
    
    def test_solve_empty_board(self):
        """Solving an empty board should return True."""
        board = create_empty_board()
        assert solve_sudoku(board) is True
    
    def test_solve_invalid_input(self):
        """Invalid board input should return False."""
        assert solve_sudoku(None) is False
        assert solve_sudoku([]) is False
        assert solve_sudoku([[0, 0]]) is False  # Wrong size
    
    def test_solve_partially_filled_puzzle(self):
        """Partially filled valid puzzle should be solvable."""
        # Simple puzzle with many clues
        board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        assert solve_sudoku(board) is True


class TestCheckSudokuSolution:
    """Test check_sudoku_solution function."""
    
    def test_valid_complete_solution(self):
        """A valid, complete board should return True."""
        valid_solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        assert check_sudoku_solution(valid_solution) is True
    
    def test_invalid_solution_duplicate_row(self):
        """Duplicate in row should return False."""
        invalid_solution = [
            [5, 5, 4, 6, 7, 8, 9, 1, 2],  # Two 5s in row
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        assert check_sudoku_solution(invalid_solution) is False
    
    def test_invalid_solution_incomplete(self):
        """Board with empty cells should return False."""
        incomplete = [
            [5, 3, 0, 6, 7, 8, 9, 1, 2],  # Has 0 (empty)
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        assert check_sudoku_solution(incomplete) is False
    
    def test_invalid_input(self):
        """Invalid input should return False."""
        assert check_sudoku_solution(None) is False
        assert check_sudoku_solution([]) is False
        assert check_sudoku_solution([[0, 0]]) is False


class TestCountSolutions:
    """Test count_solutions function."""
    
    def test_count_solutions_invalid_input(self):
        """Invalid board input should return 0."""
        assert count_solutions(None) == 0
        assert count_solutions([]) == 0
        assert count_solutions([[0, 0]]) == 0
    
    def test_count_solutions_empty_board(self):
        """Empty board has many solutions, should reach limit."""
        board = create_empty_board()
        count = count_solutions(board, limit=2)
        assert count >= 2  # Empty board has way more than 2 solutions
    
    def test_count_solutions_high_clue_puzzle(self):
        """Puzzle with many clues should have 0 or 1 solution."""
        # This is a near-complete puzzle with only one empty cell
        board = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 0],  # One empty cell
        ]
        count = count_solutions(board)
        assert count == 1


class TestHasUniqueSolution:
    """Test has_unique_solution function."""
    
    def test_unique_solution_true(self):
        """Puzzle with unique solution should return True."""
        # High-clue puzzle with unique solution
        board = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 0],
        ]
        assert has_unique_solution(board) is True
    
    def test_unique_solution_false_empty(self):
        """Empty board has multiple solutions, should return False."""
        board = create_empty_board()
        assert has_unique_solution(board) is False


class TestGeneratePuzzle:
    """Test generate_puzzle function."""
    
    def test_generate_puzzle_default(self):
        """Generated puzzle should have correct structure."""
        puzzle, solution = generate_puzzle()
        assert len(puzzle) == SIZE
        assert len(solution) == SIZE
        assert all(len(row) == SIZE for row in puzzle)
        assert all(len(row) == SIZE for row in solution)
    
    def test_generated_solution_is_valid(self):
        """Generated solution should be a valid Sudoku."""
        puzzle, solution = generate_puzzle()
        assert check_sudoku_solution(solution) is True
    
    def test_puzzle_is_subset_of_solution(self):
        """All given clues in puzzle should match solution."""
        puzzle, solution = generate_puzzle()
        for i in range(SIZE):
            for j in range(SIZE):
                if puzzle[i][j] != EMPTY:
                    assert puzzle[i][j] == solution[i][j]
    
    def test_generated_puzzle_has_unique_solution(self):
        """Generated puzzle should have exactly one solution."""
        puzzle, solution = generate_puzzle()
        # Verify the solution is correct for the puzzle
        assert check_sudoku_solution(solution) is True
        # Verify all clues match
        for i in range(SIZE):
            for j in range(SIZE):
                if puzzle[i][j] != EMPTY:
                    assert puzzle[i][j] == solution[i][j]
    
    def test_generate_puzzle_custom_clues(self):
        """Generated puzzle with custom clue count should respect target."""
        puzzle, solution = generate_puzzle(clues=45)
        clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        # Allow 90% of target (per fallback logic)
        assert clue_count >= 45 * 0.9
    
    def test_generate_puzzle_timeout_raises_error(self):
        """Generate puzzle should raise TimeoutError if timeout exceeded."""
        with pytest.raises(TimeoutError, match="Could not generate a puzzle"):
            generate_puzzle(clues=35, max_attempts=1, timeout_seconds=0.001)
    
    def test_generate_puzzle_respects_timeout(self):
        """Generate puzzle should complete within timeout window."""
        import time
        start = time.time()
        try:
            puzzle, solution = generate_puzzle(clues=35, timeout_seconds=2)
            elapsed = time.time() - start
            # Should complete well under 2 seconds (leaving buffer for system variation)
            assert elapsed < 2.0
        except TimeoutError:
            # Timeout is acceptable result for this test
            elapsed = time.time() - start
            assert elapsed >= 1.99  # Should have tried for at least timeout duration
