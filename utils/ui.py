"""User interface helpers for the Flashcard Quizzer."""

from typing import Any

from utils.quiz_engine import Card


class Colors:
    """ANSI color codes for terminal output."""

    GREEN: str = "\033[92m"
    RED: str = "\033[91m"
    BLUE: str = "\033[94m"
    YELLOW: str = "\033[93m"
    RESET: str = "\033[0m"
    BOLD: str = "\033[1m"


def display_card(card: "Card") -> None:
    """Display a flashcard's front side.

    Args:
        card: The flashcard to display.
    """
    print(f"\n{Colors.BOLD}{Colors.BLUE}Question:{Colors.RESET}")
    print(f"  {card['front']}")


def display_feedback(correct: bool, answer: str = "") -> None:
    """Display feedback for user's answer with color.

    Args:
        correct: Whether the answer was correct.
        answer: The correct answer (displayed if incorrect).
    """
    if correct:
        print(f"{Colors.GREEN}✓ Correct!{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Incorrect{Colors.RESET}")
        if answer:
            print(f"  Answer: {answer}")


def display_summary(stats: dict[str, Any]) -> None:
    """Display quiz summary with statistics table.

    Args:
        stats: Dictionary containing quiz statistics with keys:
            - total: Total number of questions
            - correct: Number of correct answers
            - incorrect_cards: List of cards answered incorrectly
    """
    total: int = stats.get("total", 0)
    correct: int = stats.get("correct", 0)
    incorrect_cards: list[Card] = stats.get("incorrect_cards", [])

    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}Quiz Summary{Colors.RESET}")
    print("=" * 60)

    if total == 0:
        print("No questions attempted.")
        return

    accuracy: float = (correct / total) * 100

    print(f"Total Questions:  {total}")
    print(f"Correct:          {correct}")
    print(f"Incorrect:        {total - correct}")

    if accuracy >= 80:
        accuracy_color = Colors.GREEN
    elif accuracy >= 60:
        accuracy_color = Colors.YELLOW
    else:
        accuracy_color = Colors.RED

    print(f"Accuracy:         {accuracy_color}{accuracy:.1f}%{Colors.RESET}")

    if incorrect_cards:
        print("\n" + "-" * 60)
        print(f"{Colors.BOLD}Terms You Missed:{Colors.RESET}")
        print("-" * 60)
        for i, card in enumerate(incorrect_cards, 1):
            print(f"{i:2}. {card['front']}")
            print(f"    Answer: {card['back']}")

    print("=" * 60)
