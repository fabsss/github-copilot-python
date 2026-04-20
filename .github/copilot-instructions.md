# Sudoku Game Project Guidelines

## Code Style

### Python Guidelines
- Follow **PEP 8** style guide strictly
- Use descriptive variable and function names (≥3 characters, avoid single letters except in comprehensions)
- Add **Google-style docstrings** to all functions and classes
- Organize the Flask app into logical, reusable components with clear separation of concerns
- Use meaningful error messages in exceptions for debugging and user feedback

### Code Quality
- Write defensive code with input validation at API/endpoint boundaries (not function-level)
- Handle edge cases explicitly
- Plan for graceful error handling with appropriate user-facing feedback messages
- Use type hints where beneficial for complex logic

## Architecture & Design

### Modern Responsive Design
- Implement responsive layouts that work across desktop, tablet, and mobile devices
- Use CSS Flexbox or Grid for layout
- Test on multiple screen sizes (mobile ≥320px, tablet ≥768px, desktop ≥1024px)

### Accessibility
- Follow **WCAG 2.1 AA** standards
- Ensure color contrast ratios ≥4.5:1 for normal text
- Provide keyboard navigation support for all interactive elements
- Use semantic HTML5 elements (`<button>`, `<nav>`, `<section>`, etc.)

## Testing

- Write unit tests using **pytest** framework
- Test **all new functions** (complete coverage for the refactored codebase)
- Test both happy paths and edge cases
- Use descriptive test names that explain what is being tested (e.g., `test_validate_sudoku_with_invalid_input_returns_false`)
- Mock external dependencies; avoid integration test dependencies in unit tests
- Test game logic: Sudoku generation, solution verification, hint system, difficulty levels, timer accuracy

## Documentation
- Always update the #README.md with new features, instructions, and any architectural decisions

## Version Control
- Use meaningful commit messages that describe the change (e.g., "Refactor Sudoku generation logic to ensure unique solutions")
- Commit frequently with small, focused changes
- Use branches for new features or refactoring work, and merge back to main with pull requests that include code review and testing

## Build and Test

### Installation
```bash
pip install -r requirements.txt
```

### Run Flask App
```bash
python app.py
```

### Run Tests
```bash
pytest
```

## Conventions

### Game Features (Per Project Requirements)
- Implement Sudoku board generator with valid puzzles and unique solutions
- Add difficulty selector (easy, medium, hard) affecting puzzle generation
- Implement solution checker that verifies user input against generated solution
- Add timer to track solve time and display in Top 10 scores
- Implement hint system that highlights valid entries with distinctive colors
- Persist Top 10 scores in browser local storage with: user name, time taken, hints used, difficulty level
- Provide immediate feedback on invalid entries (highlight, validation message)
- Show congratulatory message upon completion with time and hints used stats

### File Structure
```
starter/
├── app.py              # Flask application and routes
├── sudoku_logic.py     # Core game logic (generation, solving, validation)
├── requirements.txt    # Python dependencies
├── tests/              # Test suite
│   ├── __init__.py     # Test package marker
│   ├── test_app.py     # Flask endpoint and route tests
│   └── test_sudoku_logic.py  # Game logic unit tests
├── static/
│   ├── main.js        # JavaScript game logic and UI interactions
│   └── styles.css     # Responsive styles
└── templates/
    └── index.html     # Game interface template
```

### Error Messages
- Return clear, actionable error messages to users (not stack traces)
- Log exceptions server-side for debugging
- Handle invalid Sudoku input gracefully with specific feedback
