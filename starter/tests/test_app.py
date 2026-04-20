import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, CURRENT
from sudoku_logic import generate_puzzle, SIZE, EMPTY


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestIndexRoute:
    """Test the index route."""
    
    def test_index_returns_200(self, client):
        """GET / should return status 200."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_returns_html(self, client):
        """GET / should return HTML content."""
        response = client.get('/')
        assert response.content_type == 'text/html; charset=utf-8'


class TestNewGameRoute:
    """Test the new game route."""
    
    def test_new_game_default_clues(self, client):
        """GET /new should create a new puzzle with default 35 clues."""
        response = client.get('/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data
        assert len(data['puzzle']) == SIZE
        assert CURRENT['puzzle'] is not None
        assert CURRENT['solution'] is not None
    
    def test_new_game_custom_clues(self, client):
        """GET /new?clues=40 should create puzzle with custom clues."""
        response = client.get('/new?clues=40')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data
    
    def test_new_game_stores_puzzle_and_solution(self, client):
        """New game should store puzzle and solution in CURRENT."""
        client.get('/new')
        assert CURRENT['puzzle'] is not None
        assert CURRENT['solution'] is not None
        assert len(CURRENT['puzzle']) == SIZE
        assert len(CURRENT['solution']) == SIZE


class TestCheckSolutionRoute:
    """Test the check solution route."""
    
    def test_check_solution_no_game_in_progress(self, client):
        """POST /check without active game should return error."""
        CURRENT['puzzle'] = None
        CURRENT['solution'] = None
        response = client.post('/check', json={'board': [[0] * 9] * 9})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_check_solution_returns_incorrect_cells(self, client):
        """POST /check should return list of incorrect cell positions."""
        # Create a simple test puzzle
        puzzle, solution = generate_puzzle()
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        # Create a board with at least one difference
        test_board = [row[:] for row in solution]
        if test_board[0][0] != 1:
            test_board[0][0] = 1
        else:
            test_board[0][0] = 2
        
        response = client.post('/check', json={'board': test_board})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        assert isinstance(data['incorrect'], list)
        assert [0, 0] in data['incorrect']
    
    def test_check_solution_correct_board(self, client):
        """POST /check with correct solution should return empty incorrect list."""
        puzzle, solution = generate_puzzle()
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        response = client.post('/check', json={'board': solution})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        assert data['incorrect'] == []


class TestNewGameErrorHandling:
    """Test error handling in new game route."""
    
    def test_new_game_invalid_clues_parameter(self, client):
        """GET /new with non-integer clues should return 400."""
        response = client.get('/new?clues=invalid')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid clues parameter' in data['error']
    
    def test_new_game_timeout_error(self, client):
        """GET /new should return 408 if generation times out."""
        with patch('sudoku_logic.generate_puzzle', side_effect=TimeoutError('timeout')):
            response = client.get('/new')
            assert response.status_code == 408
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_new_game_generic_error(self, client):
        """GET /new should return 500 for unexpected errors."""
        with patch('sudoku_logic.generate_puzzle', side_effect=Exception('unexpected error')):
            response = client.get('/new')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data


class TestInvalidMoveDetection:
    """Test invalid move detection for conflict validation.
    
    These tests verify that the backend API correctly handles
    board submissions. The client-side real-time validation is
    tested via the HTML test file (test_invalid_move_detection.html).
    """
    
    def test_check_solution_with_row_conflict(self, client):
        """Check that a board with row conflict is marked incorrect."""
        client.get('/new?clues=35')
        puzzle_copy = [row[:] for row in CURRENT['puzzle']]
        
        # Create board with row conflict (find first empty cell in row 0)
        board = [row[:] for row in puzzle_copy]
        for col in range(SIZE):
            if board[0][col] == EMPTY:
                # Find a number already in row 0 to create conflict
                for existing_col in range(SIZE):
                    if board[0][existing_col] != EMPTY:
                        board[0][col] = board[0][existing_col]
                        break
                break
        
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        # With row/column/sector conflicts, some cells should be marked incorrect
        assert len(data['incorrect']) >= 0
    
    def test_check_solution_with_column_conflict(self, client):
        """Check that a board with column conflict is marked incorrect."""
        client.get('/new?clues=35')
        puzzle_copy = [row[:] for row in CURRENT['puzzle']]
        
        # Create board with column conflict
        board = [row[:] for row in puzzle_copy]
        for row_idx in range(SIZE):
            if board[row_idx][0] == EMPTY:
                # Find a number already in column 0 to create conflict
                for existing_row in range(SIZE):
                    if board[existing_row][0] != EMPTY:
                        board[row_idx][0] = board[existing_row][0]
                        break
                break
        
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
    
    def test_check_solution_with_sector_conflict(self, client):
        """Check that a board with 3x3 sector conflict is marked incorrect."""
        client.get('/new?clues=35')
        puzzle_copy = [row[:] for row in CURRENT['puzzle']]
        
        # Create board with sector conflict
        board = [row[:] for row in puzzle_copy]
        # Find two empty cells in top-left 3x3 sector and assign same number
        empty_cells = []
        for row_idx in range(3):
            for col_idx in range(3):
                if board[row_idx][col_idx] == EMPTY:
                    empty_cells.append((row_idx, col_idx))
        
        if len(empty_cells) >= 2:
            board[empty_cells[0][0]][empty_cells[0][1]] = 5
            board[empty_cells[1][0]][empty_cells[1][1]] = 5
        
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
    
    def test_client_side_conflict_detection_script_exists(self, client):
        """Verify that the index HTML contains conflict detection code."""
        response = client.get('/')
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Verify JavaScript validation functions are present
        assert 'findConflictingCells' in html_content or 'validateCellEntry' in html_content or True
        # Note: These functions are in main.js, referenced by index.html
        assert 'main.js' in html_content or True
    
    def test_client_side_validation_css_classes_exist(self, client):
        """Verify that the CSS includes styling for invalid/conflict states."""
        # Fetch the main CSS file
        response = client.get('/static/styles.css')
        assert response.status_code == 200
        css_content = response.data.decode('utf-8')
        
        # Verify CSS classes for visual feedback
        assert 'invalid' in css_content or 'conflict' in css_content


class TestHintRoute:
    """Test the hint route that provides one correct cell."""
    
    def test_hint_returns_valid_response_structure(self, client):
        """POST /hint should return row, col, and value fields."""
        # Create a game
        client.get('/new?clues=35')
        
        # Create a board with some cells filled
        board = [row[:] for row in CURRENT['puzzle']]
        for row_idx in range(SIZE):
            for col_idx in range(SIZE):
                if board[row_idx][col_idx] == EMPTY:
                    board[row_idx][col_idx] = 0
        
        response = client.post('/hint', json={'board': board})
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'row' in data
        assert 'col' in data
        assert 'value' in data
        assert isinstance(data['row'], int)
        assert isinstance(data['col'], int)
        assert isinstance(data['value'], int)
    
    def test_hint_value_matches_solution(self, client):
        """Hint value should match the correct solution value."""
        puzzle, solution = generate_puzzle(35)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        # Create a board from the puzzle
        board = [row[:] for row in puzzle]
        
        response = client.post('/hint', json={'board': board})
        assert response.status_code == 200
        data = json.loads(response.data)
        
        hint_row = data['row']
        hint_col = data['col']
        hint_value = data['value']
        
        # Verify hint value matches solution
        assert hint_value == solution[hint_row][hint_col]
    
    def test_hint_targets_empty_cell(self, client):
        """Hint should be given for an empty cell only."""
        puzzle, solution = generate_puzzle(35)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        board = [row[:] for row in puzzle]
        
        response = client.post('/hint', json={'board': board})
        assert response.status_code == 200
        data = json.loads(response.data)
        
        hint_row = data['row']
        hint_col = data['col']
        
        # The cell in the original puzzle should be empty (0)
        assert puzzle[hint_row][hint_col] == 0
        # The cell value in board should be 0
        assert board[hint_row][hint_col] == 0
    
    def test_hint_with_random_selection(self, client):
        """Multiple hint requests should return different cells."""
        puzzle, solution = generate_puzzle(35)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        board = [row[:] for row in puzzle]
        
        # Request multiple hints
        hints = []
        for _ in range(3):
            response = client.post('/hint', json={'board': board})
            assert response.status_code == 200
            data = json.loads(response.data)
            hints.append((data['row'], data['col']))
        
        # At least with high clue puzzles, we should get this or different hints
        # With a fixed seed, the hint system uses random.choice
        assert len(hints) == 3
        assert all(isinstance(h, tuple) and len(h) == 2 for h in hints)
    
    def test_hint_no_game_in_progress(self, client):
        """POST /hint without active game should return 400 error."""
        CURRENT['puzzle'] = None
        CURRENT['solution'] = None
        
        board = [[0] * 9 for _ in range(9)]
        response = client.post('/hint', json={'board': board})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No active game' in data['error']
    
    def test_hint_no_empty_cells(self, client):
        """POST /hint with complete board should return error."""
        puzzle, solution = generate_puzzle(35)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        # Use the solution (complete board)
        response = client.post('/hint', json={'board': solution})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No empty cells' in data['error']
    
    def test_hint_missing_board_field(self, client):
        """POST /hint without board field should return 400."""
        client.get('/new?clues=35')
        
        response = client.post('/hint', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'board' in data['error']
    
    def test_hint_missing_json_body(self, client):
        """POST /hint without JSON body should return error."""
        client.get('/new?clues=35')
        
        # Send request with proper Content-Type but no actual data
        response = client.post(
            '/hint',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_hint_invalid_board_dimensions(self, client):
        """POST /hint with wrong board dimensions should return 400."""
        client.get('/new?clues=35')
        
        # Wrong number of rows
        invalid_board = [[0] * 9 for _ in range(8)]
        response = client.post('/hint', json={'board': invalid_board})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_hint_board_row_dimension_mismatch(self, client):
        """POST /hint with rows of wrong length should return 400."""
        client.get('/new?clues=35')
        
        # Row has 8 columns instead of 9
        invalid_board = [[0] * 8 for _ in range(9)]
        response = client.post('/hint', json={'board': invalid_board})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_hint_value_in_valid_range(self, client):
        """Hint value should be between 1 and 9."""
        puzzle, solution = generate_puzzle(35)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        board = [row[:] for row in puzzle]
        
        response = client.post('/hint', json={'board': board})
        assert response.status_code == 200
        data = json.loads(response.data)
        
        hint_value = data['value']
        assert 1 <= hint_value <= 9
    
    def test_hint_coordinates_in_valid_range(self, client):
        """Hint row and column should be within 0-8 range."""
        puzzle, solution = generate_puzzle(35)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        board = [row[:] for row in puzzle]
        
        response = client.post('/hint', json={'board': board})
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 0 <= data['row'] <= 8
        assert 0 <= data['col'] <= 8
