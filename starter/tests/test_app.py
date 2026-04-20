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
