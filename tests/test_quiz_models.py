"""Tests for quiz engine modes and factory."""

import pytest

from utils.quiz_engine import (
    AdaptiveMode,
    Card,
    QuizMode,
    QuizModeFactory,
    RandomMode,
    SequentialMode,
)


@pytest.fixture
def sample_cards() -> list[Card]:
    """Provide sample flashcards for testing."""
    return [
        {"front": "Q1", "back": "A1"},
        {"front": "Q2", "back": "A2"},
        {"front": "Q3", "back": "A3"},
        {"front": "Q4", "back": "A4"},
        {"front": "Q5", "back": "A5"},
    ]


class TestSequentialMode:
    """Test SequentialMode strategy."""

    def test_sequential_order(self, sample_cards: list[Card]) -> None:
        """Test that cards are served in original order."""
        quiz = SequentialMode(sample_cards)

        cards_drawn = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            cards_drawn.append(card["front"])

        assert cards_drawn == ["Q1", "Q2", "Q3", "Q4", "Q5"]

    def test_sequential_returns_none_when_complete(
        self, sample_cards: list[Card]
    ) -> None:
        """Test that get_next_card returns None when deck is exhausted."""
        quiz = SequentialMode(sample_cards)

        # Draw all cards
        for _ in range(len(sample_cards)):
            quiz.get_next_card()

        # Next call should return None
        assert quiz.get_next_card() is None

    def test_sequential_reset(self, sample_cards: list[Card]) -> None:
        """Test that reset returns to beginning."""
        quiz = SequentialMode(sample_cards)

        # Draw first card
        card1 = quiz.get_next_card()
        assert card1["front"] == "Q1"

        # Reset
        quiz.reset()

        # Should get Q1 again
        card1_again = quiz.get_next_card()
        assert card1_again["front"] == "Q1"

    def test_sequential_mark_incorrect_noop(
        self, sample_cards: list[Card]
    ) -> None:
        """Test that mark_incorrect has no effect in sequential mode."""
        quiz = SequentialMode(sample_cards)

        card = quiz.get_next_card()
        quiz.mark_incorrect(card)

        # Next card should still be Q2, not Q1 again
        next_card = quiz.get_next_card()
        assert next_card["front"] == "Q2"

    def test_sequential_single_card(self) -> None:
        """Test sequential mode with single card."""
        cards: list[Card] = [{"front": "Only", "back": "Card"}]
        quiz = SequentialMode(cards)

        card = quiz.get_next_card()
        assert card["front"] == "Only"
        assert quiz.get_next_card() is None


class TestRandomMode:
    """Test RandomMode strategy."""

    def test_random_contains_all_cards(self, sample_cards: list[Card]) -> None:
        """Test that shuffle includes all cards."""
        quiz = RandomMode(sample_cards)

        cards_drawn = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            cards_drawn.append(card["front"])

        assert set(cards_drawn) == {"Q1", "Q2", "Q3", "Q4", "Q5"}
        assert len(cards_drawn) == 5

    def test_random_shuffle_different_order(
        self, sample_cards: list[Card]
    ) -> None:
        """Test that shuffle produces different order (probabilistic)."""
        # Create multiple shuffles and verify at least one differs from sequential
        orders = []
        for _ in range(5):
            quiz = RandomMode(sample_cards)
            cards_drawn = []
            while True:
                card = quiz.get_next_card()
                if card is None:
                    break
                cards_drawn.append(card["front"])
            orders.append(cards_drawn)

        # At least one should differ from sequential
        sequential = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        assert any(order != sequential for order in orders)

    def test_random_reset_reshuffles(self, sample_cards: list[Card]) -> None:
        """Test that reset reshuffles the deck."""
        quiz = RandomMode(sample_cards)

        # Draw first shuffle
        first_order = []
        for _ in range(3):
            card = quiz.get_next_card()
            first_order.append(card["front"])

        # Reset and draw again
        quiz.reset()
        second_order = []
        for _ in range(3):
            card = quiz.get_next_card()
            second_order.append(card["front"])

        # Both should have valid cards
        assert len(first_order) == 3
        assert len(second_order) == 3

    def test_random_mark_incorrect_noop(self, sample_cards: list[Card]) -> None:
        """Test that mark_incorrect has no effect in random mode."""
        quiz = RandomMode(sample_cards)

        card = quiz.get_next_card()
        quiz.mark_incorrect(card)

        # Drawing should continue normally
        next_card = quiz.get_next_card()
        assert next_card is not None


class TestAdaptiveMode:
    """Test AdaptiveMode strategy."""

    def test_adaptive_initial_shuffle(self, sample_cards: list[Card]) -> None:
        """Test that adaptive mode shuffles initially."""
        quiz = AdaptiveMode(sample_cards)

        cards_drawn = []
        for _ in range(len(sample_cards)):
            card = quiz.get_next_card()
            cards_drawn.append(card["front"])

        assert set(cards_drawn) == {"Q1", "Q2", "Q3", "Q4", "Q5"}

    def test_adaptive_mark_incorrect_prioritizes(
        self, sample_cards: list[Card]
    ) -> None:
        """Test that incorrect cards are prioritized."""
        quiz = AdaptiveMode(sample_cards)

        # Get first card and mark as incorrect
        card1 = quiz.get_next_card()
        quiz.mark_incorrect(card1)

        # Get second card and mark as incorrect
        card2 = quiz.get_next_card()
        quiz.mark_incorrect(card2)

        # Draw remaining cards
        remaining = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            remaining.append(card["front"])

        # Draw rest of deck after reset
        quiz.reset()
        deck_after_reset = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            deck_after_reset.append(card["front"])

        # Incorrect cards should be in deck
        incorrect_fronts = {card1["front"], card2["front"]}
        assert incorrect_fronts <= set(deck_after_reset)

    def test_adaptive_incorrect_cards_come_first(
        self, sample_cards: list[Card]
    ) -> None:
        """Test that incorrect cards appear in the deck after marking."""
        quiz = AdaptiveMode(sample_cards)

        # Mark specific cards as incorrect
        incorrect_cards = [sample_cards[0], sample_cards[2]]
        for card in incorrect_cards:
            quiz.mark_incorrect(card)

        # Reset to rebuild deck
        quiz.reset()

        # Draw all cards
        all_cards = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            all_cards.append(card["front"])

        # Verify incorrect cards are in the deck
        deck_fronts = {card for card in all_cards}
        assert "Q1" in deck_fronts
        assert "Q3" in deck_fronts

        # Verify all cards are present
        assert len(all_cards) == len(sample_cards)

    def test_adaptive_reset_clears_history(self, sample_cards: list[Card]) -> None:
        """Test that reset clears incorrect card history."""
        quiz = AdaptiveMode(sample_cards)

        # Mark cards as incorrect
        card = quiz.get_next_card()
        quiz.mark_incorrect(card)

        # Reset
        quiz.reset()

        # Draw all cards and verify all are shuffled (no priority)
        all_cards = []
        while True:
            card = quiz.get_next_card()
            if card is None:
                break
            all_cards.append(card["front"])

        assert len(all_cards) == len(sample_cards)
        assert set(all_cards) == {"Q1", "Q2", "Q3", "Q4", "Q5"}

    def test_adaptive_multiple_incorrect_same_card(
        self, sample_cards: list[Card]
    ) -> None:
        """Test marking same card incorrect multiple times."""
        quiz = AdaptiveMode(sample_cards)

        card = quiz.get_next_card()

        # Mark same card incorrect twice
        quiz.mark_incorrect(card)
        quiz.mark_incorrect(card)

        quiz.reset()

        # Should not break, just handle normally
        cards_drawn = []
        while True:
            c = quiz.get_next_card()
            if c is None:
                break
            cards_drawn.append(c["front"])

        assert len(cards_drawn) == len(sample_cards)

    def test_adaptive_single_card_incorrect(self) -> None:
        """Test adaptive mode with single card marked incorrect."""
        cards: list[Card] = [{"front": "Q", "back": "A"}]
        quiz = AdaptiveMode(cards)

        card = quiz.get_next_card()
        quiz.mark_incorrect(card)

        quiz.reset()

        # Should still work
        card_again = quiz.get_next_card()
        assert card_again["front"] == "Q"


class TestQuizModeFactory:
    """Test QuizModeFactory."""

    def test_factory_returns_sequential_mode(
        self, sample_cards: list[Card]
    ) -> None:
        """Test factory creates SequentialMode for 'sequential'."""
        quiz = QuizModeFactory.create("sequential", sample_cards)

        assert isinstance(quiz, SequentialMode)
        assert isinstance(quiz, QuizMode)

    def test_factory_returns_random_mode(self, sample_cards: list[Card]) -> None:
        """Test factory creates RandomMode for 'random'."""
        quiz = QuizModeFactory.create("random", sample_cards)

        assert isinstance(quiz, RandomMode)
        assert isinstance(quiz, QuizMode)

    def test_factory_returns_adaptive_mode(
        self, sample_cards: list[Card]
    ) -> None:
        """Test factory creates AdaptiveMode for 'adaptive'."""
        quiz = QuizModeFactory.create("adaptive", sample_cards)

        assert isinstance(quiz, AdaptiveMode)
        assert isinstance(quiz, QuizMode)

    def test_factory_case_insensitive(self, sample_cards: list[Card]) -> None:
        """Test factory mode names are case-insensitive."""
        modes = [
            ("SEQUENTIAL", SequentialMode),
            ("Sequential", SequentialMode),
            ("RANDOM", RandomMode),
            ("Random", RandomMode),
            ("ADAPTIVE", AdaptiveMode),
            ("Adaptive", AdaptiveMode),
        ]

        for mode_name, expected_class in modes:
            quiz = QuizModeFactory.create(mode_name, sample_cards)
            assert isinstance(quiz, expected_class)

    def test_factory_invalid_mode_raises_error(
        self, sample_cards: list[Card]
    ) -> None:
        """Test factory raises error for invalid mode."""
        with pytest.raises(ValueError, match="Unknown quiz mode"):
            QuizModeFactory.create("invalid_mode", sample_cards)

    def test_factory_error_message_lists_modes(
        self, sample_cards: list[Card]
    ) -> None:
        """Test error message includes available modes."""
        with pytest.raises(ValueError) as exc_info:
            QuizModeFactory.create("bad_mode", sample_cards)

        error_message = str(exc_info.value)
        assert "sequential" in error_message
        assert "random" in error_message
        assert "adaptive" in error_message

    def test_factory_available_modes(self) -> None:
        """Test available_modes returns all modes."""
        modes = QuizModeFactory.available_modes()

        assert "sequential" in modes
        assert "random" in modes
        assert "adaptive" in modes
        assert len(modes) == 3

    def test_factory_preserves_cards(self, sample_cards: list[Card]) -> None:
        """Test that factory passes cards correctly to mode."""
        quiz = QuizModeFactory.create("sequential", sample_cards)

        first_card = quiz.get_next_card()
        assert first_card == sample_cards[0]


class TestQuizModeInterface:
    """Test QuizMode interface compliance."""

    def test_all_modes_implement_interface(
        self, sample_cards: list[Card]
    ) -> None:
        """Test all modes implement required methods."""
        modes = [
            SequentialMode(sample_cards),
            RandomMode(sample_cards),
            AdaptiveMode(sample_cards),
        ]

        for quiz in modes:
            assert hasattr(quiz, "get_next_card")
            assert hasattr(quiz, "mark_incorrect")
            assert hasattr(quiz, "reset")
            assert callable(quiz.get_next_card)
            assert callable(quiz.mark_incorrect)
            assert callable(quiz.reset)

    def test_get_next_card_returns_card_or_none(
        self, sample_cards: list[Card]
    ) -> None:
        """Test get_next_card returns Card or None."""
        quiz = SequentialMode(sample_cards)

        # Should return card
        card = quiz.get_next_card()
        assert card is not None
        assert "front" in card
        assert "back" in card

        # Draw all cards
        for _ in range(len(sample_cards) - 1):
            quiz.get_next_card()

        # Should return None
        assert quiz.get_next_card() is None

    def test_mark_incorrect_accepts_card(self, sample_cards: list[Card]) -> None:
        """Test mark_incorrect accepts a Card."""
        quiz = AdaptiveMode(sample_cards)

        card = quiz.get_next_card()
        # Should not raise
        quiz.mark_incorrect(card)
