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

// Game state
let hintsUsed = 0;
let currentDifficulty = 'medium';
const TOP_10_SCORES_KEY = 'sudoku_top_10_scores';
const DARK_MODE_KEY = 'sudoku_dark_mode';

/**
 * Initialize dark mode by loading saved preference.
 * Called on page load to apply theme.
 */
function initializeDarkMode() {
  try {
    const savedDarkMode = localStorage.getItem(DARK_MODE_KEY);
    const isDarkMode = savedDarkMode === 'true';
    applyDarkMode(isDarkMode);
  } catch (e) {
    // localStorage might not be available, default to light mode
    applyDarkMode(false);
  }
}

/**
 * Apply dark mode to the document.
 * 
 * Args:
 *     isDarkMode: Boolean indicating if dark mode should be active.
 */
function applyDarkMode(isDarkMode) {
  if (isDarkMode) {
    document.body.setAttribute('data-theme', 'dark');
  } else {
    document.body.removeAttribute('data-theme');
  }
  updateDarkModeButtonIcon(isDarkMode);
}

/**
 * Toggle dark mode on and off, saving preference to localStorage.
 */
function toggleDarkMode() {
  try {
    const isDarkMode = document.body.getAttribute('data-theme') === 'dark';
    const newMode = !isDarkMode;
    applyDarkMode(newMode);
    localStorage.setItem(DARK_MODE_KEY, newMode ? 'true' : 'false');
  } catch (e) {
    // If localStorage fails, still toggle the theme visually
    const isDarkMode = document.body.getAttribute('data-theme') === 'dark';
    applyDarkMode(!isDarkMode);
  }
}

/**
 * Update the dark mode button icon based on current theme.
 * 
 * Args:
 *     isDarkMode: Boolean indicating if dark mode is active.
 */
function updateDarkModeButtonIcon(isDarkMode) {
  const btn = document.getElementById('dark-mode-toggle');
  if (btn) {
    btn.textContent = isDarkMode ? '☀️' : '🌙';
    btn.setAttribute('aria-label', isDarkMode ? 'Switch to light mode' : 'Switch to dark mode');
  }
}

/**
 * Get the numeric rank value for difficulty level.
 * 
 * Args:
 *     difficulty: The difficulty level ('easy', 'medium', or 'hard').
 * 
 * Returns:
 *     3 for hard, 2 for medium, 1 for easy.
 */
function getDifficultyRank(difficulty) {
  const ranks = { hard: 3, medium: 2, easy: 1 };
  return ranks[difficulty] || 1;
}

/**
 * Compare two scores for ranking purposes.
 * Higher is better (hard > medium > easy, then lower time, then lower hints).
 * 
 * Args:
 *     scoreA: First score object {name, time, difficulty, hints}.
 *     scoreB: Second score object {name, time, difficulty, hints}.
 * 
 * Returns:
 *     Positive if scoreA ranks higher, negative if scoreB ranks higher, 0 if equal.
 */
function compareScores(scoreA, scoreB) {
  const rankA = getDifficultyRank(scoreA.difficulty);
  const rankB = getDifficultyRank(scoreB.difficulty);
  
  if (rankA !== rankB) {
    return rankB - rankA;  // Higher difficulty rank is better
  }
  if (scoreA.time !== scoreB.time) {
    return scoreA.time - scoreB.time;  // Lower time is better
  }
  return scoreA.hints - scoreB.hints;  // Lower hints is better
}

/**
 * Save a game score to the Top 10 list in local storage.
 * 
 * Args:
 *     name: Player name.
 *     time: Time in seconds.
 *     difficulty: Difficulty level ('easy', 'medium', or 'hard').
 *     hints: Number of hints used.
 * 
 * Returns:
 *     The rank (1-10) achieved, or -1 if not in top 10.
 */
function saveScore(name, time, difficulty, hints) {
  let scores = loadScores();
  
  const newScore = { name, time, difficulty, hints };
  scores.push(newScore);
  
  // Sort by ranking criteria
  scores.sort(compareScores);
  
  // Keep only top 10
  scores = scores.slice(0, 10);
  
  // Save to local storage
  localStorage.setItem(TOP_10_SCORES_KEY, JSON.stringify(scores));
  
  // Return rank achievement, or -1 if not top 10
  const rank = scores.findIndex(s => s.name === name && s.time === time && s.difficulty === difficulty && s.hints === hints);
  return rank >= 0 ? rank + 1 : -1;
}

/**
 * Load all scores from local storage.
 * 
 * Returns:
 *     Array of score objects, or empty array if none saved.
 */
function loadScores() {
  const stored = localStorage.getItem(TOP_10_SCORES_KEY);
  return stored ? JSON.parse(stored) : [];
}

/**
 * Display the Top 10 scores list.
 */
function displayTopScores() {
  const scores = loadScores();
  const scoresContainer = document.getElementById('top-scores-list');
  if (!scoresContainer) return;
  
  if (scores.length === 0) {
    scoresContainer.innerHTML = '<p class="no-scores">No scores saved yet. Play a game to get started!</p>';
    return;
  }
  
  let html = '<table class="scores-table"><thead><tr><th>Rank</th><th>Name</th><th>Time</th><th>Difficulty</th><th>Hints</th></tr></thead><tbody>';
  
  scores.forEach((score, idx) => {
    const difficultyClass = `difficulty-${score.difficulty}`;
    html += `
      <tr>
        <td class="rank">${idx + 1}</td>
        <td class="name">${escapeHtml(score.name)}</td>
        <td class="time">${formatTime(score.time)}</td>
        <td class="difficulty ${difficultyClass}">${score.difficulty.toUpperCase()}</td>
        <td class="hints">${score.hints}</td>
      </tr>
    `;
  });
  
  html += '</tbody></table>';
  scoresContainer.innerHTML = html;
}

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
      const blockRow = Math.floor(i / SECTOR_SIZE);
      const blockCol = Math.floor(j / SECTOR_SIZE);
      const blockParity = (blockRow + blockCol) % 2 === 0 ? 'block-even' : 'block-odd';
      input.className = `sudoku-cell ${blockParity}`;
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
      const blockRow = Math.floor(i / SECTOR_SIZE);
      const blockCol = Math.floor(j / SECTOR_SIZE);
      const blockParity = (blockRow + blockCol) % 2 === 0 ? 'block-even' : 'block-odd';
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = `sudoku-cell prefilled ${blockParity}`;
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = `sudoku-cell ${blockParity}`;
      }
    }
  }
}

async function newGame() {
  try {
    const difficulty = document.getElementById('difficulty')?.value || 'medium';
    currentDifficulty = difficulty;  // Track the current difficulty
    hintsUsed = 0;  // Reset hints counter
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
      
      // Show success message with score saving
      const scoreMessage = `🎉 Congratulations! You solved it in ${timeString} with ${hintsUsed} hints!`;
      showSuccessMessageWithScoreSave(scoreMessage, timeElapsed, currentDifficulty, hintsUsed);
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
    
    hintsUsed++;  // Increment hints counter
    
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

/**
 * Show success message and prompt for name to save score to Top 10.
 * 
 * Args:
 *     message: The congratulation message to display.
 *     time: Time taken in seconds.
 *     difficulty: The difficulty level.
 *     hints: Number of hints used.
 */
function showSuccessMessageWithScoreSave(message, time, difficulty, hints) {
  const container = document.getElementById('message-container');
  if (container) {
    container.innerHTML = `
      <div class="message message-success">
        <p>${escapeHtml(message)}</p>
        <div class="score-save-prompt">
          <input type="text" id="player-name" placeholder="Enter your name" maxlength="20">
          <button id="save-score-btn">Save Score</button>
          <button id="skip-save-btn">Skip</button>
        </div>
      </div>
    `;
    
    const saveBtn = document.getElementById('save-score-btn');
    const skipBtn = document.getElementById('skip-save-btn');
    const nameInput = document.getElementById('player-name');
    
    saveBtn.addEventListener('click', () => {
      const name = nameInput.value.trim();
      if (!name) {
        alert('Please enter a name');
        return;
      }
      
      const rank = saveScore(name, time, difficulty, hints);
      displayTopScores();
      
      if (rank > 0 && rank <= 10) {
        showSuccessMessage(`✨ Your score has been saved! You placed #${rank} in the Top 10!`);
      }
    });
    
    skipBtn.addEventListener('click', () => {
      clearMessage();
    });
    
    // Set focus to input for better UX
    nameInput.focus();
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
  // Initialize dark mode
  initializeDarkMode();
  
  // Setup dark mode toggle button
  const darkModeBtn = document.getElementById('dark-mode-toggle');
  if (darkModeBtn) {
    darkModeBtn.addEventListener('click', toggleDarkMode);
  }
  
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', getHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  
  // Handle difficulty selector changes
  const difficultySelect = document.getElementById('difficulty');
  if (difficultySelect) {
    difficultySelect.addEventListener('change', newGame);
  }
  
  // Display Top 10 scores
  displayTopScores();
  
  // Initialize game
  newGame();
});