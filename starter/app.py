"""Flask application for Sudoku game.

This module provides REST API endpoints for the Sudoku game including:
- Puzzle generation with configurable difficulty
- Solution validation
- Game state management
"""

from typing import Dict, List, Tuple, Any, Optional
import logging
from flask import Flask, render_template, jsonify, request

import sudoku_logic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Constants
DEFAULT_CLUES = 35
MIN_CLUES = 17
MAX_CLUES = 81

# In-memory game state storage
CURRENT: Dict[str, Optional[List[List[int]]]] = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index() -> str:
    """Render the main game interface.
    
    Returns:
        Rendered HTML template for the Sudoku game interface.
    """
    logger.info('Serving index page')
    return render_template('index.html')

@app.route('/new')
def new_game() -> Tuple[Dict[str, Any], int]:
    """Generate a new Sudoku puzzle with configurable difficulty.
    
    Query Parameters:
        clues (int, optional): Number of prefilled cells (17-81). 
                              Defaults to 35 (medium).
                              - Easy: 45 cells
                              - Medium: 35 cells
                              - Hard: 25 cells
    
    Returns:
        JSON response with:
        - puzzle: 9x9 Sudoku puzzle grid
        - solution: 9x9 solution grid
        - clues: Number of prefilled cells used
        
    Raises:
        400: Invalid input (non-integer clues, out of range)
        408: Generation timeout (unable to create valid puzzle within time limit)
        500: Unexpected server error
    """
    try:
        # Get clues parameter as string first to validate it properly
        clues_str = request.args.get('clues', default=None, type=str)
        
        # If clues parameter provided, validate it's a valid integer
        if clues_str is not None:
            try:
                clues_param = int(clues_str)
            except ValueError:
                error_msg = (
                    f'Invalid clues parameter: "{clues_str}". '
                    f'Must be an integer between {MIN_CLUES} and {MAX_CLUES}.'
                )
                logger.warning(error_msg)
                return jsonify({'error': error_msg}), 400
        else:
            clues_param = DEFAULT_CLUES
        
        # Validate clues within acceptable range
        if not (MIN_CLUES <= clues_param <= MAX_CLUES):
            error_msg = (
                f'Invalid clues value: {clues_param}. '
                f'Must be between {MIN_CLUES} and {MAX_CLUES}.'
            )
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        logger.info(f'Generating puzzle with {clues_param} clues')
        
        # Generate puzzle with timeout protection
        puzzle, solution = sudoku_logic.generate_puzzle(clues_param)
        
        # Store in game state
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        
        logger.info(f'Successfully generated puzzle with {clues_param} clues')
        
        return jsonify({
            'puzzle': puzzle,
            'solution': solution,
            'clues': clues_param
        }), 200
    
    except TimeoutError as timeout_error:
        error_msg = str(timeout_error)
        logger.warning(f'Puzzle generation timeout: {error_msg}')
        return jsonify({'error': error_msg}), 408
    
    except Exception as unexpected_error:
        error_msg = 'Failed to generate puzzle. Please try again.'
        logger.error(
            f'Unexpected error during puzzle generation: {str(unexpected_error)}',
            exc_info=True
        )
        return jsonify({'error': error_msg}), 500

@app.route('/check', methods=['POST'])
def check_solution() -> Tuple[Dict[str, Any], int]:
    """Validate the user's Sudoku solution against the generated solution.
    
    Request Body (JSON):
        board: 9x9 grid with user-entered numbers (0 for empty cells)
    
    Returns:
        JSON response with:
        - incorrect: List of [row, col] positions with incorrect values
          Empty list means solution is correct.
        - error: Error message if validation fails
        
    Raises:
        400: No active game or invalid request format
        500: Unexpected server error
    """
    try:
        # Validate request has JSON body
        if not request.json:
            error_msg = 'Request body must be JSON with board data'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Extract and validate board data
        user_board = request.json.get('board')
        if not user_board:
            error_msg = 'Missing required field: board'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Check if solution exists (game in progress)
        solution = CURRENT.get('solution')
        if solution is None:
            error_msg = 'No active game. Start a new game first.'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Validate board dimensions
        if (not isinstance(user_board, list) or 
            len(user_board) != sudoku_logic.SIZE or
            not all(len(row) == sudoku_logic.SIZE for row in user_board)):
            error_msg = f'Board must be {sudoku_logic.SIZE}x{sudoku_logic.SIZE}'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Compare user board with solution
        incorrect_cells: List[List[int]] = []
        for row_idx in range(sudoku_logic.SIZE):
            for col_idx in range(sudoku_logic.SIZE):
                if user_board[row_idx][col_idx] != solution[row_idx][col_idx]:
                    incorrect_cells.append([row_idx, col_idx])
        
        logger.info(
            f'Solution check: {len(incorrect_cells)} incorrect cells out of '
            f'{sudoku_logic.SIZE * sudoku_logic.SIZE}'
        )
        
        return jsonify({'incorrect': incorrect_cells}), 200
    
    except Exception as unexpected_error:
        error_msg = 'Error checking solution. Please try again.'
        logger.error(
            f'Unexpected error during solution check: {str(unexpected_error)}',
            exc_info=True
        )
        return jsonify({'error': error_msg}), 500

@app.route('/hint', methods=['POST'])
def get_hint() -> Tuple[Dict[str, Any], int]:
    """Provide a hint by returning an empty cell and its correct value.
    
    Request Body (JSON):
        board: 9x9 grid with current user entries (0 for empty cells)
    
    Returns:
        JSON response with:
        - row: Row index of the hinted cell
        - col: Column index of the hinted cell
        - value: The correct number to fill in
        - error: Error message if no hints available
        
    Raises:
        400: No active game or board has no empty cells
        500: Unexpected server error
    """
    try:
        # Validate request has JSON body (use silent=True to avoid raising exceptions)
        request_data = request.get_json(silent=True)
        if not request_data:
            error_msg = 'Request body must be JSON with board data'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Extract and validate board data
        user_board = request_data.get('board')
        if not user_board:
            error_msg = 'Missing required field: board'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Check if solution exists (game in progress)
        solution = CURRENT.get('solution')
        if solution is None:
            error_msg = 'No active game. Start a new game first.'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Validate board dimensions
        if (not isinstance(user_board, list) or 
            len(user_board) != sudoku_logic.SIZE or
            not all(len(row) == sudoku_logic.SIZE for row in user_board)):
            error_msg = f'Board must be {sudoku_logic.SIZE}x{sudoku_logic.SIZE}'
            logger.warning(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Find all empty cells
        empty_cells: List[Tuple[int, int]] = []
        for row_idx in range(sudoku_logic.SIZE):
            for col_idx in range(sudoku_logic.SIZE):
                if user_board[row_idx][col_idx] == 0:
                    empty_cells.append((row_idx, col_idx))
        
        # Check if there are any empty cells
        if not empty_cells:
            error_msg = 'No empty cells available. Board is complete!'
            logger.info(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Select a random empty cell
        import random
        hint_row, hint_col = random.choice(empty_cells)
        hint_value = solution[hint_row][hint_col]
        
        logger.info(
            f'Hint provided: row={hint_row}, col={hint_col}, '
            f'value={hint_value}'
        )
        
        return jsonify({
            'row': hint_row,
            'col': hint_col,
            'value': hint_value
        }), 200
    
    except Exception as unexpected_error:
        error_msg = 'Error getting hint. Please try again.'
        logger.error(
            f'Unexpected error during hint: {str(unexpected_error)}',
            exc_info=True
        )
        return jsonify({'error': error_msg}), 500


if __name__ == '__main__':
    """Run the Flask development server.
    
    Note: Only use for development. For production, use a proper WSGI server.
    """
    logger.info('Starting Sudoku Game Flask application')
    app.run(debug=True)