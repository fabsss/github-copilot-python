// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
const DIFFICULTY_CLUES = {
  easy: 45,
  medium: 35,
  hard: 25
};

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  try {
    const difficulty = document.getElementById('difficulty')?.value || 'medium';
    const clues = DIFFICULTY_CLUES[difficulty];
    
    showLoadingOverlay(true);
    clearMessage();
    
    const response = await fetch(`/new?clues=${clues}`);
    const data = await response.json();
    
    // Check for HTTP error status (408, 400, 500, etc.)
    if (!response.ok) {
      showLoadingOverlay(false);
      showErrorMessage(data.error || `Error: ${response.status}`);
      return;
    }
    
    // Check if error is in response body
    if (data.error) {
      showLoadingOverlay(false);
      showErrorMessage(data.error);
      return;
    }
    
    // Check if puzzle exists
    if (!data.puzzle) {
      showLoadingOverlay(false);
      showErrorMessage('Invalid puzzle data received. Please try again.');
      return;
    }
    
    renderPuzzle(data.puzzle);
    showLoadingOverlay(false);
  } catch (error) {
    showLoadingOverlay(false);
    showErrorMessage(`Network error: ${error.message}`);
    console.error('Game initialization error:', error);
  }
}

async function checkSolution() {
  try {
    const boardDiv = document.getElementById('sudoku-board');
    const inputs = boardDiv.getElementsByTagName('input');
    const board = [];
    for (let i = 0; i < SIZE; i++) {
      board[i] = [];
      for (let j = 0; j < SIZE; j++) {
        const idx = i * SIZE + j;
        const val = inputs[idx].value;
        board[i][j] = val ? parseInt(val, 10) : 0;
      }
    }
    const response = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await response.json();
    
    if (!response.ok || data.error) {
      showErrorMessage(data.error || 'Error checking solution');
      return;
    }
    
    const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
    for (let idx = 0; idx < inputs.length; idx++) {
      const inp = inputs[idx];
      if (inp.disabled) continue;
      inp.className = 'sudoku-cell';
      if (incorrect.has(idx)) {
        inp.className = 'sudoku-cell incorrect';
      }
    }
    if (incorrect.size === 0) {
      showSuccessMessage('🎉 Congratulations! You solved it!');
    } else {
      showErrorMessage(`${incorrect.size} cell(s) are incorrect.`);
    }
  } catch (error) {
    showErrorMessage(`Error: ${error.message}`);
    console.error('Check solution error:', error);
  }
}

function showLoadingOverlay(show) {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.style.display = show ? 'flex' : 'none';
  }
}

function showErrorMessage(message) {
  const container = document.getElementById('message-container');
  if (container) {
    container.innerHTML = `
      <div class="message message-error">
        <strong>❌ Error:</strong> ${escapeHtml(message)}
      </div>
    `;
  }
}

function showSuccessMessage(message) {
  const container = document.getElementById('message-container');
  if (container) {
    container.innerHTML = `
      <div class="message message-success">
        ${escapeHtml(message)}
      </div>
    `;
  }
}

function clearMessage() {
  const container = document.getElementById('message-container');
  if (container) {
    container.innerHTML = '';
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  
  // Handle difficulty selector changes
  const difficultySelect = document.getElementById('difficulty');
  if (difficultySelect) {
    difficultySelect.addEventListener('change', newGame);
  }
  
  // Initialize
  newGame();
});