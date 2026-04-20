const fs = require('fs');
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

function createMockInput(row, col, value = '') {
    return { value, row, col };
}

function createMockBoard(initialValues = {}) {
    const inputs = [];
    for (let i = 0; i < SIZE * SIZE; i++) {
        const row = Math.floor(i / SIZE);
        const col = i % SIZE;
        let value = '';
        if (initialValues[i] !== undefined) {
            value = initialValues[i];
        }
        inputs[i] = createMockInput(row, col, value);
    }
    return inputs;
}

// Test the failing cases
console.log('Testing: detects value in same 3x3 sector');
const inputs1 = createMockBoard({ 1: '4', 10: '4' });
console.log('Index 1:', inputs1[1], 'Index 10:', inputs1[10]);
const conflicts1 = findConflictingCells(0, 0, '4', inputs1);
console.log('Conflicts:', Array.from(conflicts1));
console.log('Expected: [1, 10], Got:', Array.from(conflicts1).sort());

console.log('\nTesting: detects value in center sector');
const inputs2 = createMockBoard({ 39: '7', 48: '7' });
console.log('Index 39:', inputs2[39], 'Index 48:', inputs2[48]);
const conflicts2 = findConflictingCells(3, 3, '7', inputs2);
console.log('Conflicts:', Array.from(conflicts2));
console.log('Expected: [39, 48], Got:', Array.from(conflicts2).sort());

console.log('\nTesting: avoids duplicate conflicts when cell is in row and column intersection');
const inputs3 = createMockBoard({ 10: '5' });
console.log('Index 10:', inputs3[10]);
const conflicts3 = findConflictingCells(0, 0, '5', inputs3);
console.log('Conflicts:', Array.from(conflicts3));
console.log('Expected size: 1, Got size:', conflicts3.size);
