"""Tests for flashcard file loading and validation."""

import json
import tempfile
from pathlib import Path

import pytest

from utils.file_handler import FlashcardFormatError, load_flashcards
from utils.quiz_engine import Card


class TestLoadFlashcardsValidFormats:
    """Test loading valid flashcard formats."""

    def test_load_object_format(self, tmp_path: Path) -> None:
        """Test loading object format with 'cards' key."""
        data = {
            "cards": [
                {"front": "Q1", "back": "A1"},
                {"front": "Q2", "back": "A2"},
            ]
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path)

        assert len(result) == 2
        assert result[0]["front"] == "Q1"
        assert result[0]["back"] == "A1"

    def test_load_array_format(self, tmp_path: Path) -> None:
        """Test loading array format (direct list of cards)."""
        data = [
            {"front": "Question 1", "back": "Answer 1"},
            {"front": "Question 2", "back": "Answer 2"},
        ]
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path)

        assert len(result) == 2
        assert result[0]["front"] == "Question 1"
        assert result[1]["back"] == "Answer 2"

    def test_return_type_is_card_list(self, tmp_path: Path) -> None:
        """Test that return type is list of Card dicts."""
        data = {"cards": [{"front": "Q", "back": "A"}]}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "front" in result[0]
        assert "back" in result[0]


class TestLoadFlashcardsInvalidJSON:
    """Test handling of invalid JSON syntax."""

    def test_malformed_json(self, tmp_path: Path) -> None:
        """Test that malformed JSON raises JSONDecodeError."""
        file_path = tmp_path / "bad.json"
        file_path.write_text("{invalid json syntax")

        with pytest.raises(json.JSONDecodeError):
            load_flashcards(file_path)

    def test_invalid_json_missing_braces(self, tmp_path: Path) -> None:
        """Test JSON with missing closing braces."""
        file_path = tmp_path / "bad.json"
        file_path.write_text('{"cards": [{"front": "Q"')

        with pytest.raises(json.JSONDecodeError):
            load_flashcards(file_path)

    def test_invalid_json_trailing_comma(self, tmp_path: Path) -> None:
        """Test JSON with invalid trailing comma."""
        file_path = tmp_path / "bad.json"
        file_path.write_text('{"cards": [{"front": "Q", "back": "A"},]}')

        with pytest.raises(json.JSONDecodeError):
            load_flashcards(file_path)


class TestLoadFlashcardsFileMissing:
    """Test handling of missing files."""

    def test_file_not_found(self) -> None:
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_flashcards("nonexistent_file.json")

    def test_file_not_found_with_path(self, tmp_path: Path) -> None:
        """Test FileNotFoundError with full path."""
        missing_path = tmp_path / "missing" / "file.json"

        with pytest.raises(FileNotFoundError):
            load_flashcards(missing_path)


class TestLoadFlashcardsStructureValidation:
    """Test validation of JSON structure."""

    def test_object_missing_cards_key(self, tmp_path: Path) -> None:
        """Test that object format without 'cards' key raises error."""
        data = {"decks": [{"front": "Q", "back": "A"}]}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        with pytest.raises(FlashcardFormatError, match="'cards' key"):
            load_flashcards(file_path)

    def test_cards_key_not_list(self, tmp_path: Path) -> None:
        """Test that 'cards' must be a list."""
        data = {"cards": "not a list"}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        with pytest.raises(FlashcardFormatError, match="list"):
            load_flashcards(file_path)

    def test_empty_cards_list(self, tmp_path: Path) -> None:
        """Test that empty cards list raises error."""
        data = {"cards": []}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        with pytest.raises(FlashcardFormatError, match="No valid flashcards"):
            load_flashcards(file_path)

    def test_json_root_must_be_array_or_object(self, tmp_path: Path) -> None:
        """Test that JSON root must be array or object."""
        file_path = tmp_path / "test.json"
        file_path.write_text('"just a string"')

        with pytest.raises(FlashcardFormatError, match="array or object"):
            load_flashcards(file_path)


class TestLoadFlashcardsMissingFields:
    """Test validation of card fields."""

    def test_card_missing_front(self, tmp_path: Path) -> None:
        """Test that card without 'front' raises error in strict mode."""
        data = {"cards": [{"back": "A1"}]}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        with pytest.raises(FlashcardFormatError, match="'front' or 'back'"):
            load_flashcards(file_path, strict=True)

    def test_card_missing_back(self, tmp_path: Path) -> None:
        """Test that card without 'back' raises error in strict mode."""
        data = {"cards": [{"front": "Q1"}]}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        with pytest.raises(FlashcardFormatError, match="'front' or 'back'"):
            load_flashcards(file_path, strict=True)

    def test_card_not_dict(self, tmp_path: Path) -> None:
        """Test that non-dict card raises error in strict mode."""
        data = {"cards": ["not a dict"]}
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        with pytest.raises(FlashcardFormatError, match="not a dictionary"):
            load_flashcards(file_path, strict=True)

    def test_skip_invalid_card_non_strict(self, tmp_path: Path) -> None:
        """Test that invalid cards are skipped in non-strict mode."""
        data = {
            "cards": [
                {"front": "Q1", "back": "A1"},
                {"front": "Q2"},  # missing back
                {"front": "Q3", "back": "A3"},
            ]
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path, strict=False)

        assert len(result) == 2
        assert result[0]["front"] == "Q1"
        assert result[1]["front"] == "Q3"

    def test_skip_multiple_invalid_cards(self, tmp_path: Path) -> None:
        """Test skipping multiple invalid cards in non-strict mode."""
        data = {
            "cards": [
                {"back": "A1"},  # missing front
                {"front": "Q2", "back": "A2"},
                "not a dict",  # not a dict
                {"front": "Q4", "back": "A4"},
            ]
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path, strict=False)

        assert len(result) == 2
        assert result[0]["front"] == "Q2"
        assert result[1]["front"] == "Q4"


class TestLoadFlashcardsTypeConversion:
    """Test type conversion and normalization."""

    def test_non_string_values_converted(self, tmp_path: Path) -> None:
        """Test that non-string front/back are converted to strings."""
        data = {
            "cards": [
                {"front": 123, "back": 456},
                {"front": True, "back": False},
            ]
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path)

        assert result[0]["front"] == "123"
        assert result[0]["back"] == "456"
        assert result[1]["front"] == "True"
        assert result[1]["back"] == "False"

    def test_extra_fields_preserved(self, tmp_path: Path) -> None:
        """Test that extra fields in cards are ignored."""
        data = {
            "cards": [
                {
                    "front": "Q1",
                    "back": "A1",
                    "difficulty": "hard",
                    "tags": ["python"],
                }
            ]
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data))

        result = load_flashcards(file_path)

        assert result[0]["front"] == "Q1"
        assert result[0]["back"] == "A1"
        # Extra fields are not included in result


class TestLoadFlashcardsEncoding:
    """Test file encoding handling."""

    def test_utf8_encoding(self, tmp_path: Path) -> None:
        """Test loading UTF-8 encoded JSON with special characters."""
        data = {
            "cards": [
                {"front": "What is café?", "back": "A coffee shop"},
                {"front": "¿Hola?", "back": "Spanish greeting"},
            ]
        }
        file_path = tmp_path / "test.json"
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        result = load_flashcards(file_path)

        assert "café" in result[0]["front"]
        assert "¿" in result[1]["front"]
