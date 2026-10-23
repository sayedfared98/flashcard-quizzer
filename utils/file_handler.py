"""Module for handling flashcard data ingestion from JSON files."""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from utils.quiz_engine import Card


class FlashcardFormatError(Exception):
    """Raised when flashcard data structure is invalid."""

    pass


def load_flashcards(filepath: str | Path, strict: bool = False) -> list["Card"]:
    """Load flashcards from a JSON file.

    Supports two JSON formats:
    - Array format: [{"front": "...", "back": "..."}]
    - Object format: {"cards": [{"front": "...", "back": "..."}]}

    Args:
        filepath: Path to the JSON file containing flashcards.
        strict: If True, raise an error on invalid cards. If False, skip them.

    Returns:
        A list of flashcard dictionaries with 'front' and 'back' keys.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        FlashcardFormatError: If the JSON structure is invalid or malformed.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Flashcard file not found: {filepath}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {filepath}: {e.msg}",
            e.doc,
            e.pos,
        ) from e

    cards = _extract_cards(data, filepath)
    validated_cards = _validate_cards(cards, filepath, strict)

    if not validated_cards:
        raise FlashcardFormatError("No valid flashcards found in the file")

    return validated_cards


def _extract_cards(data: Any, filepath: str | Path) -> list[Any]:
    """Extract cards list from JSON data (supports both formats).

    Args:
        data: Parsed JSON data.
        filepath: Path to the file (for error messages).

    Returns:
        List of card objects.

    Raises:
        FlashcardFormatError: If the JSON structure is invalid.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if "cards" not in data:
            raise FlashcardFormatError(
                f"{filepath}: Object format requires a 'cards' key"
            )
        cards = data["cards"]
        if not isinstance(cards, list):
            raise FlashcardFormatError(f"{filepath}: 'cards' value must be a list")
        return cards

    raise FlashcardFormatError(
        f"{filepath}: JSON root must be an array or object with 'cards' key"
    )


def _validate_cards(
    cards: list[Any], filepath: str | Path, strict: bool = False
) -> list["Card"]:
    """Validate and extract flashcards from a list.

    Args:
        cards: List of card objects to validate.
        filepath: Path to the file (for error messages).
        strict: If True, raise on invalid cards. If False, skip them.

    Returns:
        List of validated flashcard dictionaries.

    Raises:
        FlashcardFormatError: If strict mode is enabled and validation fails.
    """
    validated_cards: list["Card"] = []

    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            error_msg = f"{filepath}: Card at index {idx} is not a dictionary"
            if strict:
                raise FlashcardFormatError(error_msg)
            continue

        if "front" not in card or "back" not in card:
            error_msg = f"{filepath}: Card at index {idx} missing 'front' or 'back'"
            if strict:
                raise FlashcardFormatError(error_msg)
            continue

        validated_cards.append({"front": str(card["front"]), "back": str(card["back"])})

    return validated_cards
