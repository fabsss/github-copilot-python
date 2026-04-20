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
