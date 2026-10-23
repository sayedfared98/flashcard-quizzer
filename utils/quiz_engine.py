"""Quiz engine using strategy and factory patterns for different quiz modes."""

import random
from abc import ABC, abstractmethod
from typing import Optional, TypedDict


class Card(TypedDict):
    """Type definition for a flashcard."""

    front: str
    back: str


class QuizMode(ABC):
    """Abstract base class defining the quiz mode interface."""

    def __init__(self, cards: list[Card]) -> None:
        """Initialize quiz mode with a deck of cards.

        Args:
            cards: List of flashcards to quiz.
        """
        self.cards: list[Card] = cards
        self.current_index: int = 0

    @abstractmethod
    def get_next_card(self) -> Optional[Card]:
        """Get the next card in the quiz sequence.

        Returns:
            Next card or None if quiz is complete.
        """
        pass

    @abstractmethod
    def mark_incorrect(self, card: Card) -> None:
        """Mark a card as incorrectly answered.

        Args:
            card: The card that was answered incorrectly.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the quiz mode to its initial state."""
        pass


class SequentialMode(QuizMode):
    """Strategy: Serves cards in their original order."""

    def get_next_card(self) -> Optional[Card]:
        """Get the next card in sequential order."""
        if self.current_index < len(self.cards):
            card = self.cards[self.current_index]
            self.current_index += 1
            return card
        return None

    def mark_incorrect(self, card: Card) -> None:
        """No special handling for incorrect cards in sequential mode."""
        pass

    def reset(self) -> None:
        """Reset to the beginning of the deck."""
        self.current_index = 0


class RandomMode(QuizMode):
    """Strategy: Shuffles the deck and serves cards in random order."""

    def __init__(self, cards: list[Card]) -> None:
        """Initialize random mode with shuffled deck.

        Args:
            cards: List of flashcards to shuffle.
        """
        super().__init__(cards)
        self.shuffled_cards: list[Card] = cards.copy()
        random.shuffle(self.shuffled_cards)

    def get_next_card(self) -> Optional[Card]:
        """Get the next card from the shuffled deck."""
        if self.current_index < len(self.shuffled_cards):
            card = self.shuffled_cards[self.current_index]
            self.current_index += 1
            return card
        return None

    def mark_incorrect(self, card: Card) -> None:
        """No special handling for incorrect cards in random mode."""
        pass

    def reset(self) -> None:
        """Reset to the beginning of the shuffled deck."""
        self.current_index = 0
        self.shuffled_cards = self.cards.copy()
        random.shuffle(self.shuffled_cards)


class AdaptiveMode(QuizMode):
    """Strategy: Prioritizes cards previously answered incorrectly."""

    def __init__(self, cards: list[Card]) -> None:
        """Initialize adaptive mode.

        Args:
            cards: List of flashcards to quiz.
        """
        super().__init__(cards)
        self.incorrect_indices: set[int] = set()
        self.deck: list[Card] = []
        self._build_adaptive_deck()

    def _build_adaptive_deck(self) -> None:
        """Build deck with incorrect cards prioritized."""
        incorrect_cards: list[Card] = [
            self.cards[i] for i in self.incorrect_indices
        ]
        correct_cards: list[Card] = [
            self.cards[i]
            for i in range(len(self.cards))
            if i not in self.incorrect_indices
        ]
        random.shuffle(correct_cards)
        self.deck = incorrect_cards + correct_cards
        self.current_index = 0

    def get_next_card(self) -> Optional[Card]:
        """Get the next card, prioritizing incorrect ones."""
        if self.current_index < len(self.deck):
            card = self.deck[self.current_index]
            self.current_index += 1
            return card
        return None

    def mark_incorrect(self, card: Card) -> None:
        """Mark a card as incorrect and rebuild deck.

        Args:
            card: The card that was answered incorrectly.
        """
        for i, c in enumerate(self.cards):
            if c == card:
                self.incorrect_indices.add(i)
                self._build_adaptive_deck()
                return

    def reset(self) -> None:
        """Reset adaptive mode, clearing incorrect card history."""
        self.incorrect_indices = set()
        self._build_adaptive_deck()


class QuizModeFactory:
    """Factory for creating quiz mode instances using the factory pattern."""

    _modes: dict[str, type[QuizMode]] = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @classmethod
    def create(cls, mode: str, cards: list[Card]) -> QuizMode:
        """Create a quiz mode instance.

        Args:
            mode: Quiz mode name ('sequential', 'random', or 'adaptive').
            cards: List of flashcards for the quiz.

        Returns:
            QuizMode instance of the requested type.

        Raises:
            ValueError: If the mode name is not recognized.
        """
        mode_lower: str = mode.lower()
        if mode_lower not in cls._modes:
            available: str = ", ".join(cls._modes.keys())
            raise ValueError(
                f"Unknown quiz mode '{mode}'. " f"Available modes: {available}"
            )
        return cls._modes[mode_lower](cards)

    @classmethod
    def available_modes(cls) -> list[str]:
        """Get a list of all available quiz modes.

        Returns:
            List of available mode names.
        """
        return list(cls._modes.keys())
