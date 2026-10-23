# Flashcard Quizzer

> A sophisticated command-line learning tool that delivers adaptive flashcard quizzes with intelligent question prioritization and real-time performance analytics.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Tests](https://img.shields.io/badge/Tests-62%2F62%20passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen.svg)
![Code Quality](https://img.shields.io/badge/Code%20Quality-Flake8%20%7C%20Black%20%7C%20Mypy-blue.svg)

## Overview

Flashcard Quizzer is a production-ready Python CLI application designed for efficient learning through spaced repetition. Load your own flashcard decks from JSON, choose your preferred quiz strategy (sequential, random, or adaptive), and get immediate feedback with color-coded results. Perfect for language learning, exam preparation, or skill development.

### Key Features

- **📋 Flexible Format Support**: Load flashcards from either array or object-wrapped JSON formats
- **🎯 Three Quiz Modes**:
  - **Sequential**: Cards in their original order
  - **Random**: Shuffled deck for varied learning
  - **Adaptive**: Intelligently prioritizes cards you struggle with
- **✨ Real-time Feedback**: Color-coded terminal output (green for correct, red for incorrect)
- **📊 Session Analytics**: Accuracy percentage, total questions, and list of missed terms
- **🛡️ Robust Error Handling**: Friendly error messages instead of stack traces
- **♿ Graceful Exit**: Type `exit` or press Ctrl+C without stack traces
- **🔤 Case-Insensitive Matching**: Flexible answer acceptance

## Quick Start

### Installation

1. **Clone or download this repository**
   ```bash
   cd /voc/work/project/starter
   ```

2. **Create a Python virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```

### Usage

**View help**
```bash
python main.py --help
```

**Run a quiz in sequential mode (default)**
```bash
python main.py -f data/python_basics.json
```

**Run with random shuffled deck**
```bash
python main.py --file data/glossary.json --mode random
```

**Run in adaptive mode (recommended for learning)**
```bash
python main.py -f data/python_basics.json -m adaptive
```

### Sample Interaction

```
Starting quiz with 8 cards in sequential mode...

Question:
  Which keyword defines a function?
Your answer: def
✓ Correct!

Question:
  Which built-in function returns the length of a list?
Your answer: len
✓ Correct!

Question:
  What is the boolean type called?
Your answer: boolean
✗ Incorrect
  Answer: bool

...

============================================================
Quiz Summary
============================================================
Total Questions:  8
Correct:          7
Incorrect:        1
Accuracy:         87.5%

------------------------------------------------------------
Terms You Missed:
------------------------------------------------------------
 1. What is the boolean type called?
    Answer: bool
============================================================
```

## Project Structure

```
.
├── main.py                          # CLI entry point with argparse
├── utils/
│   ├── __init__.py
│   ├── file_handler.py             # JSON loading & validation
│   ├── quiz_engine.py              # Strategy & Factory patterns
│   └── ui.py                       # Terminal display with colors
├── tests/
│   ├── test_flashcard_loader.py    # 20 tests for file handling
│   ├── test_quiz_models.py         # 27 tests for quiz modes
│   └── test_integration.py         # 15 end-to-end tests
├── data/
│   ├── python_basics.json          # Sample deck (object format)
│   └── glossary.json               # Sample deck (array format)
├── docs/
│   ├── ai_edit_log.md             # AI collaboration log
│   ├── report_template.md         # Project report
│   ├── CODE_QUALITY_GUIDE.md      # Quality standards reference
│   └── QUALITY_STANDARDS_COMMANDS.md  # Commands cheat sheet
└── requirements.txt                # Python dependencies
```

## Architecture

### Design Patterns

**Strategy Pattern** (`utils/quiz_engine.py`)
- Abstract `QuizMode` base class defines the quiz interface
- Three concrete strategies implement different delivery methods:
  - `SequentialMode`: Serves cards in original order
  - `RandomMode`: Shuffles deck using Fisher-Yates algorithm
  - `AdaptiveMode`: Tracks incorrect cards and prioritizes them
- Each mode encapsulates its own state and logic, making the code highly maintainable

**Factory Pattern** (`QuizModeFactory`)
- Centralized mode instantiation via `QuizModeFactory.create(mode_string, cards)`
- Case-insensitive mode selection ("ADAPTIVE", "adaptive", "Adaptive" all work)
- Easy to extend: adding a new mode requires only creating the class and updating the factory mapping
- Provides helpful error messages listing available modes

### Why This Architecture?

Compared to conditional logic spread throughout the main loop, this design provides:
- **Loose Coupling**: Main loop depends only on the `QuizMode` interface, not implementations
- **Open/Closed Principle**: Easy to add new modes without modifying existing code
- **Single Responsibility**: Each mode class handles exactly one quiz strategy
- **Testability**: Each mode can be tested independently with unit tests
- **Maintainability**: Developers can understand each mode by reading one focused class

## Code Quality

### Testing

**62 comprehensive tests achieving 99% code coverage:**

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m coverage run -m pytest tests/
python -m coverage report

# Run specific test file
python -m pytest tests/test_quiz_models.py -v
```

**Test organization:**
- `test_flashcard_loader.py` (20 tests): File loading, JSON validation, error handling
- `test_quiz_models.py` (27 tests): Quiz modes, factory pattern, interface compliance
- `test_integration.py` (15 tests): End-to-end flows, statistics calculation, edge cases

### Code Standards

All code meets strict quality standards:

```bash
# PEP 8 compliance (zero errors)
python -m flake8 utils/ main.py --max-line-length=88 --extend-ignore=E203,W503

# Automatic formatting
python -m black --check utils/ main.py

# Type safety (strict mode)
python -m mypy utils/ main.py --strict
```

**Current Status:**
- ✅ Flake8: 0 errors (PEP 8 compliant)
- ✅ Black: All files properly formatted
- ✅ Mypy: Strict type checking passed
- ✅ Coverage: 99% (exceeds 80% requirement)

### Type Hints

Complete type coverage throughout the codebase:
- All function signatures include parameter and return types
- Card data uses TypedDict for clarity
- Union types avoided in favor of simpler data structures
- Passes `mypy --strict` validation

## Supported JSON Formats

### Array Format
```json
[
  {"front": "What is 2+2?", "back": "4"},
  {"front": "What is the capital of France?", "back": "Paris"}
]
```

### Object Format
```json
{
  "cards": [
    {"front": "What is 2+2?", "back": "4"},
    {"front": "What is the capital of France?", "back": "Paris"}
  ]
}
```

Both formats are fully supported. Mix them in your `data/` folder as needed.

## Creating Your Own Decks

1. Create a JSON file in the `data/` directory:
   ```bash
   touch data/my_deck.json
   ```

2. Add flashcards using either format above

3. Run the quiz:
   ```bash
   python main.py -f data/my_deck.json
   ```

## Troubleshooting

### "Flashcard file not found"
- Ensure the file path is correct relative to where you run the command
- Try using an absolute path: `python main.py -f /full/path/to/data/my_deck.json`

### "Invalid JSON in file"
- Validate your JSON at [jsonlint.com](https://www.jsonlint.com/)
- Ensure all strings use double quotes, not single quotes
- Check for trailing commas in arrays/objects

### "Unknown quiz mode"
- Available modes are: `sequential`, `random`, `adaptive`
- Mode names are case-insensitive

### ImportError when running tests
- Ensure you've installed dependencies: `python -m pip install -r requirements.txt`
- Verify you're in the correct directory: `cd /voc/work/project/starter`

## Development Guide

### Running Quality Checks

```bash
# All checks (recommended before committing)
python -m flake8 utils/ main.py --max-line-length=88 --extend-ignore=E203,W503 && \
python -m black --check utils/ main.py && \
python -m mypy utils/ main.py --strict && \
python -m pytest tests/ -v
```

### Auto-formatting Code
```bash
python -m black utils/ main.py
```

### Viewing Test Coverage
```bash
python -m coverage run -m pytest tests/
python -m coverage report           # Terminal report
python -m coverage html             # Open htmlcov/index.html in browser
```

## Documentation

- **[CODE_QUALITY_GUIDE.md](docs/CODE_QUALITY_GUIDE.md)** - Comprehensive guide to quality standards, tools, and best practices
- **[QUALITY_STANDARDS_COMMANDS.md](docs/QUALITY_STANDARDS_COMMANDS.md)** - Quick reference for all quality check commands
- **[IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Overview of modules and features
- **[TEST_SUITE_SUMMARY.md](docs/TEST_SUITE_SUMMARY.md)** - Detailed test documentation
- **[ai_edit_log.md](docs/ai_edit_log.md)** - AI collaboration process and decisions

## Performance

- Loads typical JSON decks instantly
- Quiz loop operates in real-time with immediate feedback
- Memory efficient: handles decks of 1000+ cards smoothly
- No external dependencies beyond Python standard library and dev tools

## Technologies Used

- **Python 3.10+**: Core language with modern type hints
- **pytest**: Comprehensive testing framework
- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **Mypy**: Static type checking
- **Coverage.py**: Test coverage measurement

## License

This project is provided as part of an educational course on AI-assisted software development.

---

**Questions or Issues?** Review the documentation files in `docs/` or check the troubleshooting section above.

**Want to contribute?** Follow the code quality standards outlined in [CODE_QUALITY_GUIDE.md](docs/CODE_QUALITY_GUIDE.md).
