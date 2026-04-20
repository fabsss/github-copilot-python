const SIZE = 9;
const SECTOR_SIZE = 3;

function getSectorRow(row) {
    return Math.floor(row / SECTOR_SIZE) * SECTOR_SIZE;
}

function getSectorCol(col) {
    return Math.floor(col / SECTOR_SIZE) * SECTOR_SIZE;
}

function findConflictingCells(row, col, value, inputs) {
    const conflicts = new Set();
    if (!value || value === '') return conflicts;
    
    // Check row
    for (let c = 0; c < SIZE; c++) {
        if (c !== col) {
            const idx = row * SIZE + c;
            const cellValue = inputs[idx].value;
            if (cellValue === value) conflicts.add(idx);
        }
    }
    
    // Check column
    for (let r = 0; r < SIZE; r++) {
        if (r !== row) {
            const idx = r * SIZE + col;
            const cellValue = inputs[idx].value;
            if (cellValue === value) conflicts.add(idx);
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
                if (cellValue === value) conflicts.add(idx);
            }
        }
    }
    
    return conflicts;
}

function createMockInput(row, col, value = '') {
    return { value, row, col };
}

function createMockBoard(initialValues = {}) {
    const inputs = [];
    for (let i = 0; i < SIZE * SIZE; i++) {
        const row = Math.floor(i / SIZE);
        const col = i % SIZE;
        inputs[i] = createMockInput(row, col, initialValues[i] || '');
    }
    return inputs;
}

let testCount = 0, passCount = 0, failCount = 0;

function test(name, fn) {
    testCount++;
    try {
        fn();
        passCount++;
        console.log('[PASS] ' + name);
    } catch (error) {
        failCount++;
        console.log('[FAIL] ' + name + ': ' + error.message);
    }
}

function assert(condition, msg) {
    if (!condition) throw new Error(msg);
}

function assertEqual(actual, expected, msg) {
    if (actual !== expected) throw new Error(msg + ' (expected ' + expected + ', got ' + actual + ')');
}

// Run all tests
console.log('=== Testing getSectorRow ===');
test('getSectorRow: row 0 returns 0', () => assertEqual(getSectorRow(0), 0, 'Row 0'));
test('getSectorRow: row 3 returns 3', () => assertEqual(getSectorRow(3), 3, 'Row 3'));
test('getSectorRow: row 6 returns 6', () => assertEqual(getSectorRow(6), 6, 'Row 6'));

console.log('\n=== Testing getSectorCol ===');
test('getSectorCol: col 0 returns 0', () => assertEqual(getSectorCol(0), 0, 'Col 0'));
test('getSectorCol: col 3 returns 3', () => assertEqual(getSectorCol(3), 3, 'Col 3'));
test('getSectorCol: col 6 returns 6', () => assertEqual(getSectorCol(6), 6, 'Col 6'));

console.log('\n=== Testing findConflictingCells - Row conflicts ===');
test('detects value in same row', () => {
    const inputs = createMockBoard({ 0: '5', 1: '3' });
    const conflicts = findConflictingCells(0, 2, '5', inputs);
    assert(conflicts.has(0), 'Should find conflict at index 0');
    assertEqual(conflicts.size, 1, 'Should have exactly 1 conflict');
});

test('detects multiple values in same row', () => {
    const inputs = createMockBoard({ 4: '7', 7: '7' });
    const conflicts = findConflictingCells(0, 0, '7', inputs);
    assert(conflicts.has(4), 'Should find conflict at index 4');
    assert(conflicts.has(7), 'Should find conflict at index 7');
    assertEqual(conflicts.size, 2, 'Should have exactly 2 conflicts');
});

console.log('\n=== Testing findConflictingCells - Column conflicts ===');
test('detects value in same column', () => {
    const inputs = createMockBoard({ 9: '5', 18: '5' });
    const conflicts = findConflictingCells(0, 0, '5', inputs);
    assert(conflicts.has(9), 'Should find conflict at index 9');
    assertEqual(conflicts.size, 1, 'Should have exactly 1 conflict');
});

test('detects multiple values in same column', () => {
    const inputs = createMockBoard({ 9: '3', 36: '3' });
    const conflicts = findConflictingCells(0, 0, '3', inputs);
    assert(conflicts.has(9), 'Should find conflict at index 9');
    assert(conflicts.has(36), 'Should find conflict at index 36');
    assertEqual(conflicts.size, 2, 'Should have exactly 2 conflicts');
});

console.log('\n=== Testing findConflictingCells - Sector conflicts ===');
test('detects value in same 3x3 sector', () => {
    const inputs = createMockBoard({ 1: '4', 10: '4' });
    const conflicts = findConflictingCells(0, 0, '4', inputs);
    console.log('  -> Index 1 at (0,1), Index 10 at (' + Math.floor(10/9) + ',' + (10%9) + ')');
    console.log('  -> Conflicts found:', Array.from(conflicts));
    assert(conflicts.has(1), 'Should find conflict at index 1');
    assert(conflicts.has(10), 'Should find conflict at index 10');
    assertEqual(conflicts.size, 2, 'Should have exactly 2 conflicts');
});

test('detects value in center sector', () => {
    const inputs = createMockBoard({ 39: '7', 48: '7' });
    const conflicts = findConflictingCells(3, 3, '7', inputs);
    console.log('  -> Index 39 at (' + Math.floor(39/9) + ',' + (39%9) + '), Index 48 at (' + Math.floor(48/9) + ',' + (48%9) + ')');
    console.log('  -> Conflicts found:', Array.from(conflicts));
    assert(conflicts.has(39), 'Should find conflict at index 39');
    assert(conflicts.has(48), 'Should find conflict at index 48');
});

console.log('\n=== Testing findConflictingCells - Edge cases ===');
test('returns empty set for empty value', () => {
    const inputs = createMockBoard({ 0: '5' });
    const conflicts = findConflictingCells(0, 1, '', inputs);
    assertEqual(conflicts.size, 0, 'Should return empty set for empty value');
});

test('handles empty board', () => {
    const inputs = createMockBoard();
    const conflicts = findConflictingCells(4, 4, '5', inputs);
    assertEqual(conflicts.size, 0, 'Should return empty set for empty board');
});

console.log('\n=== Testing findConflictingCells - Deduplication ===');
test('avoids duplicate when at row-col intersection', () => {
    const inputs = createMockBoard({ 10: '5' });
    const conflicts = findConflictingCells(0, 0, '5', inputs);
    console.log('  -> Index 10 at (' + Math.floor(10/9) + ',' + (10%9) + ')');
    console.log('  -> Conflicts found:', Array.from(conflicts), 'Size:', conflicts.size);
    assertEqual(conflicts.size, 1, 'Should count intersection cell only once');
});

test('avoids duplicate in sector already counted', () => {
    const inputs = createMockBoard({ 1: '5' });
    const conflicts = findConflictingCells(0, 0, '5', inputs);
    console.log('  -> Index 1 at (0,1)');
    console.log('  -> Conflicts found:', Array.from(conflicts), 'Size:', conflicts.size);
    assertEqual(conflicts.size, 1, 'Should count cell only once');
});

console.log('\n' + '='.repeat(40));
console.log('Total Tests: ' + testCount);
console.log('Passed: ' + passCount);
console.log('Failed: ' + failCount);

if (failCount > 0) process.exit(1);
