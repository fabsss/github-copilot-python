// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SECTOR_SIZE = 3;
let puzzle = [];
const DIFFICULTY_CLUES = {
  easy: 45,
  medium: 35,
  hard: 25
};

// Timer state
let timerInterval = null;
let elapsedSeconds = 0;

/**
 * Format elapsed seconds into MM:SS format.
 * 
 * Args:
 *     seconds: The number of elapsed seconds.
 * 
 * Returns:
 *     A string in MM:SS format.
 */
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/**
 * Start the game timer and update display every second.
 */
function startTimer() {
  elapsedSeconds = 0;
  updateTimerDisplay();
  
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    updateTimerDisplay();
  }, 1000);
}

/**
 * Update the timer display with the current elapsed time.
 */
function updateTimerDisplay() {
  const timerElement = document.getElementById('timer');
  if (timerElement) {
    timerElement.textContent = formatTime(elapsedSeconds);
  }
}

/**
 * Stop the game timer and return the elapsed time.
 * 
 * Returns:
 *     The number of elapsed seconds.
 */
function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  return elapsedSeconds;
}

/**
 * Get the top-left corner row of the 3x3 sector for a given cell.
 * 
 * Args:
 *     row: The row index of the cell.
 * 
 * Returns:
 *     The top-left corner row index of the sector.
 */
function getSectorRow(row) {
  return Math.floor(row / SECTOR_SIZE) * SECTOR_SIZE;
}

/**
 * Get the top-left corner column of the 3x3 sector for a given cell.
 * 
 * Args:
 *     col: The column index of the cell.
 * 
 * Returns:
 *     The top-left corner column index of the sector.
 */
function getSectorCol(col) {
  return Math.floor(col / SECTOR_SIZE) * SECTOR_SIZE;
}

/**
 * Find all cells that conflict with a given value in the same row, column, or sector.
 * 
 * Args:
 *     row: The row index of the cell being checked.
 *     col: The column index of the cell being checked.
 *     value: The value to check for conflicts.
 *     inputs: The array of input elements.
 * 
 * Returns:
 *     A Set of indices of conflicting cells.
 */
function findConflictingCells(row, col, value, inputs) {
  const conflicts = new Set();
  
  if (!value || value === '') return conflicts;
  
  // Check row
  for (let c = 0; c < SIZE; c++) {
    if (c !== col) {
      const idx = row * SIZE + c;
      const cellValue = inputs[idx].value;
      if (cellValue === value) {
        conflicts.add(idx);
      }
    }
  }
  
  // Check column
  for (let r = 0; r < SIZE; r++) {
    if (r !== row) {
      const idx = r * SIZE + col;
      const cellValue = inputs[idx].value;
      if (cellValue === value) {
        conflicts.add(idx);
      }
    }
  }
  
  // Check 3x3 sector
  const sectorRow = getSectorRow(row);
  const sectorCol = getSectorCol(col);
  for (let r = sectorRow; r < sectorRow + SECTOR_SIZE; r++) {
    for (let c = sectorCol; c < sectorCol + SECTOR_SIZE; c++) {
      if (r !== row || c !== col) {
        const idx = r * SIZE + c;
        const cellValue = inputs[idx].value;
        if (cellValue === value) {
          conflicts.add(idx);
        }
      }
    }
  }
  
  return conflicts;
}

/**
 * Validate a cell entry and update visual feedback for conflicts.
 * 
 * Args:
 *     cellInput: The input element of the cell being validated.
 *     inputs: The array of all input elements on the board.
 */
function validateCellEntry(cellInput, inputs) {
  const row = parseInt(cellInput.dataset.row, 10);
  const col = parseInt(cellInput.dataset.col, 10);
  const value = cellInput.value;
  
  // Remove conflicting classes from all cells
  for (let i = 0; i < inputs.length; i++) {
    inputs[i].classList.remove('invalid', 'conflict');
  }
  
  // If cell is empty, no conflicts
  if (value === '') return;
  
  // Find conflicting cells
  const conflicts = findConflictingCells(row, col, value, inputs);
  
  if (conflicts.size > 0) {
    // Mark current cell as invalid
    cellInput.classList.add('invalid');
    
    // Mark conflicting cells with conflict border
    for (const idx of conflicts) {
      inputs[idx].classList.add('conflict');
    }
  }
}

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
        
        // Validate cell entry for conflicts
        const boardDiv = document.getElementById('sudoku-board');
        const inputs = boardDiv.getElementsByTagName('input');
        validateCellEntry(e.target, inputs);
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
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
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
    stopTimer();
    
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
    startTimer();
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
      const timeElapsed = stopTimer();
      const timeString = formatTime(timeElapsed);
      showSuccessMessage(`🎉 Congratulations! You solved it in ${timeString}!`);
    } else {
      showErrorMessage(`${incorrect.size} cell(s) are incorrect.`);
    }
  } catch (error) {
    showErrorMessage(`Error: ${error.message}`);
    console.error('Check solution error:', error);
  }
}

async function getHint() {
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
    const response = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await response.json();
    
    if (!response.ok || data.error) {
      showErrorMessage(data.error || 'Error getting hint');
      return;
    }
    
    // Fill the hint cell and lock it
    const hintRow = data.row;
    const hintCol = data.col;
    const hintValue = data.value;
    const idx = hintRow * SIZE + hintCol;
    const cellInput = inputs[idx];
    
    cellInput.value = hintValue;
    cellInput.disabled = true;
    cellInput.className = 'sudoku-cell hint';
    
    showSuccessMessage('💡 Hint provided! Cell filled with the correct value.');
  } catch (error) {
    showErrorMessage(`Error: ${error.message}`);
    console.error('Get hint error:', error);
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
  document.getElementById('hint').addEventListener('click', getHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  
  // Handle difficulty selector changes
  const difficultySelect = document.getElementById('difficulty');
  if (difficultySelect) {
    difficultySelect.addEventListener('change', newGame);
  }
  
  // Initialize
  newGame();
});