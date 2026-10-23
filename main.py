"""Entry point for the Flashcard Quizzer CLI."""

import argparse
import sys
from pathlib import Path

from utils.file_handler import FlashcardFormatError, load_flashcards
from utils.quiz_engine import Card, QuizMode, QuizModeFactory
from utils.ui import display_card, display_feedback, display_summary


def load_flashcards_safely(filepath: str | Path) -> list[Card] | None:
    """Load flashcards with graceful error handling for CLI.

    Prints user-friendly error messages instead of stack traces.

    Args:
        filepath: Path to the JSON flashcard file.

    Returns:
        List of flashcards on success, None on error.
    """
    try:
        cards = load_flashcards(filepath)
        return cards
    except FileNotFoundError:
        print(f"Error: Flashcard file not found: {filepath}", file=sys.stderr)
        return None
    except FlashcardFormatError as e:
        print(f"Error: Invalid flashcard format: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Failed to load flashcards: {e}", file=sys.stderr)
        return None


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Flashcard Quizzer - Learn with spaced repetition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -f data/python_basics.json
  python main.py -f data/glossary.json -m adaptive
  python main.py --file data/python_basics.json --mode random
        """,
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to JSON flashcard file",
        metavar="FILE",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="sequential",
        help="Quiz mode: sequential, random, or adaptive",
        metavar="MODE",
    )
    return parser.parse_args()


def run_quiz(quiz: QuizMode) -> dict[str, int | list[Card]]:
    """Run the main quiz loop.

    Args:
        quiz: QuizMode instance to run.

    Returns:
        Dictionary with quiz statistics.
    """
    total: int = 0
    correct: int = 0
    incorrect_cards: list[Card] = []

    try:
        while True:
            card: Card | None = quiz.get_next_card()
            if card is None:
                break

            total += 1
            display_card(card)

            try:
                user_answer: str = input("Your answer: ").strip()
            except EOFError:
                break

            if user_answer.lower() == "exit":
                print("\nQuiz ended.")
                break

            is_correct: bool = user_answer.lower() == card["back"].lower()

            if is_correct:
                correct += 1
                display_feedback(correct=True)
            else:
                incorrect_cards.append(card)
                display_feedback(correct=False, answer=card["back"])
                quiz.mark_incorrect(card)

    except KeyboardInterrupt:
        print("\n\nQuiz interrupted.")

    return {
        "total": total,
        "correct": correct,
        "incorrect_cards": incorrect_cards,
    }


def main() -> None:
    """Main entry point for the application."""
    args: argparse.Namespace = parse_arguments()

    cards: list[Card] | None = load_flashcards_safely(args.file)
    if cards is None:
        sys.exit(1)

    try:
        quiz: QuizMode = QuizModeFactory.create(args.mode, cards)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Starting quiz with {len(cards)} cards in {args.mode} mode...")
    stats: dict[str, int | list[Card]] = run_quiz(quiz)
    display_summary(stats)


if __name__ == "__main__":
    main()
