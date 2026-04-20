# Refactor a Sudoku Game written in Python Flask

Use this simple Sudoku game as a starting point to practice your skills with GitHub Copilot. The goal is to refactor the code to use modern technologies, while also adding new features and improving the overall user experience.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Dependencies

```
- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3
```

### Installation

1. Fork this repository to your GitHub account. (You can use the "Fork" button on the top right corner of the repository page.)

2. Clone your forked repository to your local machine.

3. Open a terminal window and navigate to the "github-copilot-python/starter" directory.

4. Create a Python virtual environment and activate it (optional but highly recommended).

```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install required Python packages.

```bash
pip install -r requirements.txt
```

6. Run the Flask app.

```bash
python app.py
```

7. Open http://127.0.0.1:5000 in your browser.

## Features

### Real-Time Invalid Move Detection
The game provides immediate visual feedback when users enter numbers that violate Sudoku rules.

**How it works:**
- As you type a number in a cell, the game checks if it conflicts with existing entries
- **Invalid cells** (cells with conflicting values) are highlighted with an **orange background**
- **Conflicting cells** (cells that already contain the entered number) are marked with an **orange border**
- The validation checks all three constraints:
  - **Row conflicts**: Same number in the same row
  - **Column conflicts**: Same number in the same column
  - **Sector conflicts**: Same number in the same 3×3 sector
- Visual feedback is cleared when the conflict is resolved

**Technical Implementation:**
- Client-side validation in [main.js](starter/static/main.js) for instant feedback
- Functions: `getSectorRow()`, `getSectorCol()`, `findConflictingCells()`, `validateCellEntry()`
- CSS classes: `.invalid` (orange background), `.conflict` (orange border)
- No server roundtrip needed - provides seamless, responsive user experience

## Testing

This project includes a comprehensive test suite using **pytest** and browser-based unit tests to ensure code quality and functionality.

### Running Tests

Run all tests from the `starter` directory:

```bash
pytest                    # Run all tests
pytest -v               # Run with verbose output
pytest -v tests/test_app.py     # Run specific test file
pytest -v tests/test_sudoku_logic.py::TestIsValidMove  # Run specific test class
```

### Browser-Based Tests

Open the invalid move detection test suite in your browser:

```bash
# Open in browser
starter/tests/test_invalid_move_detection.html
```

This HTML test file contains **27 unit tests** for the real-time validation logic, including:
- Sector row/column calculation tests
- Row, column, and sector conflict detection tests
- Edge cases and deduplication tests
- All tests execute in the browser console

### Test Coverage

View code coverage with:

```bash
pytest --cov=app --cov=sudoku_logic --cov-report=term-missing
```

Current coverage: **98%**
- `app.py`: 97% (Flask routes and application logic)
- `sudoku_logic.py`: 98% (Sudoku game logic and utilities)

### Test Structure

Tests are organized in `starter/tests/`:

```
tests/
├── __init__.py                           # Test package marker
├── test_app.py                          # Flask route and endpoint tests (40 tests)
│   ├── TestIndexRoute                   # Index page tests
│   ├── TestNewGameRoute                 # Puzzle generation tests
│   ├── TestCheckSolutionRoute           # Solution checking tests
│   ├── TestNewGameErrorHandling         # Error handling tests
│   └── TestInvalidMoveDetection         # Invalid move detection integration tests (5 tests)
├── test_sudoku_logic.py                 # Game logic unit tests (35 tests)
└── test_invalid_move_detection.html     # Browser-based unit tests (27 tests)
```

### What's Tested

**Sudoku Logic:**
- `is_valid_move()` - Validates moves against Sudoku rules
- `solve_sudoku()` - Puzzle solving with backtracking
- `check_sudoku_solution()` - Solution verification
- `generate_puzzle()` - Puzzle generation and structure

**Flask Routes:**
- `GET /` - Index page rendering
- `GET /new` - Puzzle generation with custom difficulty
- `POST /check` - Solution checking and feedback
- Error handling for invalid requests

**Invalid Move Detection (Client-Side):**
- Conflict detection in rows, columns, and sectors
- Visual feedback application and cleanup
- Edge cases (empty values, empty board, deduplication)

Tests cover both happy paths and edge cases per project guidelines.

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. The goal is to create a more modern and maintainable codebase and add additional functionality to the final product. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.

- Errors should be handled gracefully with appropriate messages to the user.
- Implement a Sudoku board generator that creates a valid Sudoku puzzle with a unique solution.
- Add a timer to track how long it takes to solve the puzzle.
- Implement a solution checker that verifies if the user's solution is correct using event delegation.
- Add a difficulty selector to allow users to choose between easy, medium, and hard puzzles.
- Add a hint feature that provides clues for the user that are noted with unique colors.
- Add a check puzzle button that checks the current state of the board against the solution.
- User should get immediate feedback on their input, such as highlighting invalid entries.
- Top 10 scores should be saved in local storage and displayed on the page with the user's name, time taken, hints used, and difficulty level.
- The game should be responsive and work well on both desktop and mobile devices.
- UI colors should be visually appealing and accessible.
- Completed and correct puzzles should display a congratulatory message with the time taken and hints used and ask for the user's name for Top 10 times.
