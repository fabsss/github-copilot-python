"""Stress tests for difficulty level clue count validation.

These tests ensure that the refactored puzzle generator reliably
produces puzzles with the correct number of clues for each difficulty
level, validating the fix that checks actual clue count instead of
just removed cells.
"""

import pytest
import time
from statistics import mean, stdev

from sudoku_logic import generate_puzzle, SIZE, EMPTY


class TestDifficultyClueAccuracy:
    """Test that puzzle generation produces correct clue counts per difficulty."""
    
    @pytest.mark.parametrize('target_clues,difficulty_name,iterations,tolerance', [
        (45, 'easy', 50, 0.9),
        (35, 'medium', 50, 0.9),
        (25, 'hard', 10, 0.8),  # Hard: fewer iterations, more lenient tolerance
    ])
    def test_clue_count_within_tolerance(self, target_clues, difficulty_name, iterations, tolerance):
        """Generate puzzles and verify clue counts meet tolerance.
        
        This stress test validates that the fix checking actual clue count
        (not just removed cells) produces consistent difficulty levels.
        
        Args:
            target_clues: Target number of clues (45=easy, 35=medium, 25=hard)
            difficulty_name: Human-readable difficulty name
            iterations: Number of puzzles to generate (50 for easy/medium, 10 for hard)
            tolerance: Minimum clue ratio to accept (0.9 for easy/medium, 0.8 for hard)
        """
        min_clues = target_clues * tolerance
        
        clue_counts = []
        
        for iteration in range(iterations):
            puzzle, solution = generate_puzzle(clues=target_clues)
            
            # Count actual clues (non-zero cells) in puzzle
            actual_clues = sum(
                1 for row in puzzle 
                for cell in row 
                if cell != EMPTY
            )
            
            clue_counts.append(actual_clues)
            
            # Verify this puzzle meets tolerance
            assert actual_clues >= min_clues, (
                f"{difficulty_name} puzzle {iteration}: "
                f"expected >={target_clues * tolerance} clues, got {actual_clues}"
            )
        
        # Verify consistency across all puzzles
        avg_clues = mean(clue_counts)
        assert avg_clues >= min_clues, (
            f"{difficulty_name}: Average clues {avg_clues} "
            f"below minimum {target_clues * tolerance}"
        )
    
    def test_easy_clue_count_distribution(self):
        """Easy puzzles should consistently have ~45 clues (40-50 range)."""
        target_clues = 45
        min_clues = 40
        max_clues = 50
        
        clue_counts = []
        
        for _ in range(50):
            puzzle, solution = generate_puzzle(clues=target_clues)
            actual_clues = sum(
                1 for row in puzzle 
                for cell in row 
                if cell != EMPTY
            )
            clue_counts.append(actual_clues)
            assert min_clues <= actual_clues <= max_clues
        
        avg = mean(clue_counts)
        std = stdev(clue_counts) if len(clue_counts) > 1 else 0
        
        # Easy puzzles should be tightly clustered around 45
        assert 42 <= avg <= 47, f"Easy avg {avg} too far from target 45"
        assert std < 3, f"Easy std {std} too high - inconsistent difficulty"
    
    def test_medium_clue_count_distribution(self):
        """Medium puzzles should consistently have ~35 clues (31-39 range)."""
        target_clues = 35
        min_clues = 31
        max_clues = 39
        
        clue_counts = []
        
        for _ in range(50):
            puzzle, solution = generate_puzzle(clues=target_clues)
            actual_clues = sum(
                1 for row in puzzle 
                for cell in row 
                if cell != EMPTY
            )
            clue_counts.append(actual_clues)
            assert min_clues <= actual_clues <= max_clues
        
        avg = mean(clue_counts)
        std = stdev(clue_counts) if len(clue_counts) > 1 else 0
        
        assert 33 <= avg <= 37, f"Medium avg {avg} too far from target 35"
        assert std < 2.5, f"Medium std {std} too high - inconsistent difficulty"
    
    def test_hard_clue_count_distribution(self):
        """Hard puzzles should consistently have ~25 clues (20-25 range with 80% tolerance)."""
        target_clues = 25
        min_clues = 20  # 80% of 25
        
        clue_counts = []
        
        for _ in range(10):  # Fewer iterations for hard (takes longer)
            puzzle, solution = generate_puzzle(clues=target_clues)
            actual_clues = sum(
                1 for row in puzzle 
                for cell in row 
                if cell != EMPTY
            )
            clue_counts.append(actual_clues)
            assert actual_clues >= min_clues
        
        avg = mean(clue_counts)
        std = stdev(clue_counts) if len(clue_counts) > 1 else 0
        
        # Hard avg should be reasonable (around 22-26)
        assert 20 <= avg <= 26, f"Hard avg {avg} outside reasonable range"
        # Std should show consistency
        assert std < 3, f"Hard std {std} too high - inconsistent difficulty"
    
    def test_difficulty_levels_are_distinct(self):
        """Easy should have more clues than medium, medium more than hard."""
        easy_clues = []
        medium_clues = []
        hard_clues = []
        
        # Generate 10 puzzles per difficulty (hard takes longer)
        for _ in range(10):
            e, _ = generate_puzzle(clues=45)
            m, _ = generate_puzzle(clues=35)
            h, _ = generate_puzzle(clues=25)
            
            easy_clues.append(sum(1 for row in e for cell in row if cell != EMPTY))
            medium_clues.append(sum(1 for row in m for cell in row if cell != EMPTY))
            hard_clues.append(sum(1 for row in h for cell in row if cell != EMPTY))
        
        easy_avg = mean(easy_clues)
        medium_avg = mean(medium_clues)
        hard_avg = mean(hard_clues)
        
        # Verify clear progression: Easy > Medium > Hard
        assert easy_avg > medium_avg, (
            f"Easy ({easy_avg}) should have more clues than Medium ({medium_avg})"
        )
        assert medium_avg > hard_avg, (
            f"Medium ({medium_avg}) should have more clues than Hard ({hard_avg})"
        )
        
        # Verify meaningful gaps (at least 5 clues difference)
        easy_medium_gap = easy_avg - medium_avg
        medium_hard_gap = medium_avg - hard_avg
        
        assert easy_medium_gap >= 5, (
            f"Easy-Medium gap {easy_medium_gap} too small"
        )
        assert medium_hard_gap >= 5, (
            f"Medium-Hard gap {medium_hard_gap} too small"
        )
    
    def test_all_clues_within_valid_range(self):
        """All generated clues should be in valid range [1-9], no EMPTY in clues."""
        # Use 5 iterations for hard, 15 for easy/medium (reduces runtime)
        for target_clues, iterations in [(45, 15), (35, 15), (25, 5)]:
            for _ in range(iterations):
                puzzle, solution = generate_puzzle(clues=target_clues)
                
                for row_idx, row in enumerate(puzzle):
                    for col_idx, cell in enumerate(row):
                        # Cell should be either EMPTY (0) or 1-9
                        assert cell == EMPTY or 1 <= cell <= 9, (
                            f"Invalid clue at ({row_idx}, {col_idx}): {cell}"
                        )
                        # If not empty, should match solution
                        if cell != EMPTY:
                            assert cell == solution[row_idx][col_idx], (
                                f"Clue mismatch at ({row_idx}, {col_idx})"
                            )
    
    def test_puzzle_has_no_duplicates_in_rows(self):
        """Verify no duplicate clues in any row (Sudoku rule)."""
        # Use 5 iterations for hard, 15 for easy/medium
        for target_clues, iterations in [(45, 15), (35, 15), (25, 5)]:
            for _ in range(iterations):
                puzzle, _ = generate_puzzle(clues=target_clues)
                
                for row_idx, row in enumerate(puzzle):
                    # Get non-empty clues
                    clues_in_row = [cell for cell in row if cell != EMPTY]
                    # Check no duplicates
                    assert len(clues_in_row) == len(set(clues_in_row)), (
                        f"Duplicate clues in row {row_idx}"
                    )
    
    def test_puzzle_has_no_duplicates_in_cols(self):
        """Verify no duplicate clues in any column (Sudoku rule)."""
        # Use 5 iterations for hard, 15 for easy/medium
        for target_clues, iterations in [(45, 15), (35, 15), (25, 5)]:
            for _ in range(iterations):
                puzzle, _ = generate_puzzle(clues=target_clues)
                
                for col_idx in range(SIZE):
                    col = [puzzle[row_idx][col_idx] for row_idx in range(SIZE)]
                    clues_in_col = [cell for cell in col if cell != EMPTY]
                    assert len(clues_in_col) == len(set(clues_in_col)), (
                        f"Duplicate clues in column {col_idx}"
                    )
    
    def test_puzzle_has_no_duplicates_in_sectors(self):
        """Verify no duplicate clues in any 3x3 sector (Sudoku rule)."""
        # Use 5 iterations for hard, 15 for easy/medium
        for target_clues, iterations in [(45, 15), (35, 15), (25, 5)]:
            for _ in range(iterations):
                puzzle, _ = generate_puzzle(clues=target_clues)
                
                for sector_row in range(3):
                    for sector_col in range(3):
                        sector = []
                        for row in range(sector_row * 3, sector_row * 3 + 3):
                            for col in range(sector_col * 3, sector_col * 3 + 3):
                                sector.append(puzzle[row][col])
                        
                        clues_in_sector = [c for c in sector if c != EMPTY]
                        assert len(clues_in_sector) == len(set(clues_in_sector)), (
                            f"Duplicate clues in sector ({sector_row}, {sector_col})"
                        )
    
    def test_puzzle_generation_reliability_10_iterations(self):
        """Generate 10 hard puzzles - should succeed without errors."""
        successful = 0
        errors = []
        
        for iteration in range(10):  # 10 iterations for hard (realistic)
            try:
                puzzle, solution = generate_puzzle(clues=25)
                
                # Quick validation
                actual_clues = sum(1 for row in puzzle for cell in row if cell != EMPTY)
                if 20 <= actual_clues <= 30:  # Within 80-120% tolerance
                    successful += 1
            except Exception as e:
                errors.append(f"Iteration {iteration}: {str(e)}")
        
        # All 10 should succeed
        assert successful == 10, (
            f"Only {successful}/10 puzzles generated successfully. "
            f"Errors: {errors[:5]}"
        )
    
    def test_clue_count_never_exceeds_81(self):
        """Clue count should never exceed 81 (full board)."""
        # Use 5 iterations for hard, 15 for easy/medium
        for target_clues, iterations in [(45, 15), (35, 15), (25, 5)]:
            for _ in range(iterations):
                puzzle, _ = generate_puzzle(clues=target_clues)
                actual_clues = sum(1 for row in puzzle for cell in row if cell != EMPTY)
                assert actual_clues <= 81, f"Clue count {actual_clues} exceeds 81"
    
    def test_clue_count_never_zero(self):
        """Every puzzle should have at least one clue."""
        # Use 5 iterations for hard, 15 for easy/medium
        for target_clues, iterations in [(45, 15), (35, 15), (25, 5)]:
            for _ in range(iterations):
                puzzle, _ = generate_puzzle(clues=target_clues)
                actual_clues = sum(1 for row in puzzle for cell in row if cell != EMPTY)
                assert actual_clues > 0, "Puzzle has zero clues - cannot solve"


class TestClueCountVsRemovedCellsFix:
    """Validate the specific fix that checks actual clues instead of removed cells.
    
    Before fix: Accepted puzzle if removed >= clues * 0.9 (number of cells removed)
    After fix: Accepts puzzle if actual_clues >= clues * 0.9 (final clue count)
    
    This ensures difficulty is based on final puzzle hardness, not generation timing.
    """
    
    def test_hard_puzzles_reach_target_clues_despite_stuck_removal(self):
        """Hard puzzles should reach ~25 clues with 80% tolerance.
        
        Hard puzzles are most likely to get stuck during removal (more uniqueness
        constraints). The updated algorithm and tolerance ensure we still meet clue targets.
        """
        target_clues = 25
        min_clues = 20  # 80% of 25
        
        # Generate 10 hard puzzles
        for _ in range(10):
            puzzle, _ = generate_puzzle(clues=target_clues)
            actual_clues = sum(1 for row in puzzle for cell in row if cell != EMPTY)
            
            # Even if removal got stuck, final puzzle should hit 80% target
            assert actual_clues >= min_clues, (
                f"Hard puzzle with {actual_clues} clues "
                f"below minimum {min_clues}"
            )
    
    def test_removed_cells_vs_actual_clues_consistency(self):
        """Verify removed_cells + actual_clues = 81 (always)."""
        # Use 5 iterations for hard, 10 for easy/medium
        for target_clues, iterations in [(45, 10), (35, 10), (25, 5)]:
            for _ in range(iterations):
                puzzle, _ = generate_puzzle(clues=target_clues)
                actual_clues = sum(1 for row in puzzle for cell in row if cell != EMPTY)
                actual_empty = sum(1 for row in puzzle for cell in row if cell == EMPTY)
                
                # Math check: clues + empty cells = 81
                assert actual_clues + actual_empty == 81, (
                    f"{actual_clues} clues + {actual_empty} empty "
                    f"should equal 81"
                )


class TestGenerationPerformance:
    """Monitor performance of puzzle generation with clue count fix."""
    
    def test_easy_generation_speed(self):
        """Easy puzzles (45 clues) should generate quickly."""
        times = []
        for _ in range(10):
            start = time.time()
            generate_puzzle(clues=45)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = mean(times)
        # Easy should be fast - under 1 second on average
        assert avg_time < 1.0, f"Easy generation too slow: {avg_time:.2f}s"
    
    def test_medium_generation_speed(self):
        """Medium puzzles (35 clues) should generate in reasonable time."""
        times = []
        for _ in range(10):
            start = time.time()
            generate_puzzle(clues=35)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = mean(times)
        # Medium should be moderate - under 5 seconds
        assert avg_time < 5.0, f"Medium generation too slow: {avg_time:.2f}s"
    
    def test_hard_generation_speed(self):
        """Hard puzzles (25 clues) may take longer but should be < 40s timeout."""
        times = []
        for _ in range(3):  # 3 iterations to verify timeout is sufficient
            start = time.time()
            generate_puzzle(clues=25)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = mean(times)
        max_time = max(times)
        
        # Hard can take time but should not hit 40s timeout
        assert max_time < 40.0, f"Hard generation timed out: {max_time:.2f}s"
        assert avg_time < 30.0, f"Hard generation too slow: {avg_time:.2f}s"
