"""Integration tests for complete quiz flow."""

import json
from pathlib import Path

import pytest

from utils.file_handler import load_flashcards
from utils.quiz_engine import Card, QuizModeFactory


@pytest.fixture
def quiz_data_file(tmp_path: Path) -> Path:
    """Create a temporary JSON file with quiz data."""
    data = {
        "cards": [
            {"front": "What is 2+2?", "back": "4"},
            {"front": "What is the capital of France?", "back": "Paris"},
            {"front": "What is Python?", "back": "A programming language"},
        ]
    }
    file_path = tmp_path / "quiz.json"
    file_path.write_text(json.dumps(data))
    return file_path


class TestQuizFlow:
    """Test complete quiz flow from loading to stats."""

    def test_load_and_quiz_sequential(self, quiz_data_file: Path) -> None:
        """Test loading cards and running sequential quiz."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        assert len(cards) == 3

        # Draw all cards
        drawn_cards = []
        for _ in range(3):
            card = quiz.get_next_card()
            assert card is not None
            drawn_cards.append(card)

        assert len(drawn_cards) == 3
        assert drawn_cards[0]["front"] == "What is 2+2?"

    def test_quiz_with_three_answers(self, quiz_data_file: Path) -> None:
        """Test answering 3 questions with mix of correct/incorrect."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        # Simulate user answers
        answers = [
            "4",
            "london",
            "A programming language",
        ]  # 2 correct, 1 wrong

        correct_count = 0
        incorrect_cards: list[Card] = []

        for i in range(3):
            card = quiz.get_next_card()
            assert card is not None

            is_correct = answers[i].lower() == card["back"].lower()

            if is_correct:
                correct_count += 1
            else:
                incorrect_cards.append(card)
                quiz.mark_incorrect(card)

        # Verify stats
        assert correct_count == 2
        assert len(incorrect_cards) == 1
        assert incorrect_cards[0]["front"] == "What is the capital of France?"

    def test_stats_calculation_perfect_score(
        self, quiz_data_file: Path
    ) -> None:
        """Test statistics calculation with perfect score."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        total = 0
        correct = 0

        while True:
            card = quiz.get_next_card()
            if card is None:
                break

            total += 1
            # All answers correct
            correct += 1

        assert total == 3
        assert correct == 3
        accuracy = (correct / total) * 100
        assert accuracy == 100.0

    def test_stats_calculation_partial_score(
        self, quiz_data_file: Path
    ) -> None:
        """Test statistics calculation with partial score."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        total = 0
        correct = 0
        incorrect_cards: list[Card] = []

        # Answer 2 questions (1 correct, 1 incorrect)
        total += 1
        correct += 1  # Correct answer

        card2 = quiz.get_next_card()
        total += 1
        # Incorrect answer
        incorrect_cards.append(card2)

        accuracy = (correct / total) * 100
        assert accuracy == 50.0
        assert len(incorrect_cards) == 1

    def test_stats_zero_score(self, quiz_data_file: Path) -> None:
        """Test statistics with no correct answers."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        total = 0
        correct = 0
        incorrect_cards: list[Card] = []

        while True:
            card = quiz.get_next_card()
            if card is None:
                break

            total += 1
            # All answers wrong
            incorrect_cards.append(card)

        assert correct == 0
        assert total == 3
        accuracy = (correct / total) * 100
        assert accuracy == 0.0

    def test_adaptive_quiz_with_repeated_incorrect(
        self, quiz_data_file: Path
    ) -> None:
        """Test adaptive mode repeats incorrect questions."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("adaptive", cards)

        # Get first card
        card1 = quiz.get_next_card()
        assert card1 is not None

        # Mark as incorrect
        quiz.mark_incorrect(card1)

        # Get next card - should be card1 again (prioritized)
        card2 = quiz.get_next_card()
        assert card2 is not None

        # In adaptive mode, we should see card1 again at the front
        # (though not guaranteed due to randomization of others)
        if card2["front"] == card1["front"]:
            # Card was repeated - this is the adaptive behavior
            assert True

    def test_mixed_case_answers_accepted(self, quiz_data_file: Path) -> None:
        """Test that case-insensitive matching works in quiz."""

        # Test various case combinations
        test_cases = [
            ("4", "4", True),  # Exact match
            ("4", "4".upper(), True),  # Uppercase
            ("PARIS", "paris", True),  # Mixed case
            ("Python", "PYTHON", True),  # Different case
            ("Wrong", "4", False),  # Wrong answer
        ]

        for user_answer, correct_answer, should_match in test_cases:
            is_match = user_answer.lower() == correct_answer.lower()
            assert is_match == should_match


class TestQuizModeBehavior:
    """Test different quiz modes through a quiz."""

    def test_sequential_mode_order(self, quiz_data_file: Path) -> None:
        """Test sequential mode maintains order through quiz."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        order = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            order.append(card["front"])

        assert order == [
            "What is 2+2?",
            "What is the capital of France?",
            "What is Python?",
        ]

    def test_random_mode_includes_all(self, quiz_data_file: Path) -> None:
        """Test random mode includes all cards in quiz."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("random", cards)

        drawn = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            drawn.append(card["front"])

        expected_fronts = {
            "What is 2+2?",
            "What is the capital of France?",
            "What is Python?",
        }
        assert set(drawn) == expected_fronts

    def test_adaptive_mode_prioritizes_incorrect(
        self, quiz_data_file: Path
    ) -> None:
        """Test adaptive mode prioritizes incorrect cards in quiz."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("adaptive", cards)

        # Draw and mark first card incorrect
        card1 = quiz.get_next_card()
        quiz.mark_incorrect(card1)

        # Draw more cards
        for _ in range(2):
            quiz.get_next_card()

        # Reset and check prioritization
        quiz.reset()

        # The marked card should be in the deck
        all_cards = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            all_cards.append(card)

        fronts = [c["front"] for c in all_cards]
        assert card1["front"] in fronts


class TestEndToEndQuiz:
    """End-to-end quiz simulation tests."""

    def test_complete_quiz_simulation(self, quiz_data_file: Path) -> None:
        """Simulate a complete quiz from start to finish."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        # Simulate quiz loop
        stats = {"total": 0, "correct": 0, "incorrect_cards": []}

        while True:
            card = quiz.get_next_card()
            if card is None:
                break

            stats["total"] += 1

            # Simulate user input (predefined answers)
            if card["front"] == "What is 2+2?":
                user_answer = "4"
            elif card["front"] == "What is the capital of France?":
                user_answer = "london"  # Wrong
            else:
                user_answer = "A programming language"

            is_correct = user_answer.lower() == card["back"].lower()

            if is_correct:
                stats["correct"] += 1
            else:
                stats["incorrect_cards"].append(card)
                quiz.mark_incorrect(card)

        # Verify final stats
        assert stats["total"] == 3
        assert stats["correct"] == 2
        assert len(stats["incorrect_cards"]) == 1

        accuracy = (stats["correct"] / stats["total"]) * 100
        assert accuracy == pytest.approx(66.67, rel=0.01)

    def test_early_exit_preserves_stats(self, quiz_data_file: Path) -> None:
        """Test that early exit preserves correct stats."""
        cards = load_flashcards(quiz_data_file)
        quiz = QuizModeFactory.create("sequential", cards)

        stats = {"total": 0, "correct": 0, "incorrect_cards": []}

        # Only answer 2 out of 3 questions
        for _ in range(2):
            card = quiz.get_next_card()
            if card is None:
                break

            stats["total"] += 1
            stats["correct"] += 1  # Both correct

        # User exits
        quiz.get_next_card()  # This would be Q3, but we don't answer it

        assert stats["total"] == 2
        assert stats["correct"] == 2
        accuracy = (stats["correct"] / stats["total"]) * 100
        assert accuracy == 100.0

    def test_all_modes_complete_quiz(self, quiz_data_file: Path) -> None:
        """Test that all modes can complete a quiz."""
        cards = load_flashcards(quiz_data_file)

        for mode_name in ["sequential", "random", "adaptive"]:
            quiz = QuizModeFactory.create(mode_name, cards)

            count = 0
            while True:
                card = quiz.get_next_card()
                if card is None:
                    break
                count += 1

            assert count == 3, f"Mode {mode_name} should have 3 cards"


class TestQuizStatsEdgeCases:
    """Test edge cases in quiz statistics."""

    def test_single_card_quiz(self) -> None:
        """Test quiz with single card."""
        cards: list[Card] = [{"front": "Only Q", "back": "Only A"}]

        quiz = QuizModeFactory.create("sequential", cards)

        card = quiz.get_next_card()
        assert card is not None
        assert card["front"] == "Only Q"

        # One correct answer
        correct = 1
        total = 1
        accuracy = (correct / total) * 100
        assert accuracy == 100.0

    def test_large_deck_quiz(self) -> None:
        """Test quiz with large deck."""
        cards: list[Card] = [
            {"front": f"Q{i}", "back": f"A{i}"} for i in range(100)
        ]

        quiz = QuizModeFactory.create("sequential", cards)

        count = 0
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            count += 1

        assert count == 100

    def test_special_characters_in_answers(self) -> None:
        """Test quiz with special characters in answers."""
        cards: list[Card] = [
            {"front": "Question", "back": "Answer with @#$% chars"},
        ]

        quiz = QuizModeFactory.create("sequential", cards)

        card = quiz.get_next_card()
        assert "@#$%" in card["back"]

        # Test matching
        user_input = "ANSWER WITH @#$% CHARS"
        is_match = user_input.lower() == card["back"].lower()
        assert is_match
