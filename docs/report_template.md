# AI-Assisted Development Project Report

**Project Title:** Flashcard Quizzer CLI - An AI-Assisted Software Development Project  
**Date:** October 23, 2026

---

## Executive Summary

I built a command-line flashcard quiz application in Python that demonstrates professional software engineering practices and effective AI collaboration. The Flashcard Quizzer loads quiz decks from JSON files and delivers an interactive quiz experience with three distinct quiz modes: Sequential (card order), Random (shuffled deck), and Adaptive (prioritizes previously incorrect cards). The application features immediate color-coded feedback, case-insensitive answer matching, session statistics with accuracy percentages, and graceful error handling that presents friendly messages instead of stack traces. I achieved 99% test coverage with 62 passing tests, zero linting errors, and strict type checking compliance. This project demonstrates not just the application itself, but a mature approach to AI-assisted development where I leveraged Claude's code generation capabilities while maintaining rigorous quality standards through code review, type checking, and comprehensive testing.

---

## Introduction & Architecture

### What the Application Does

The Flashcard Quizzer is a learning tool that helps users study using spaced repetition principles. Users provide a JSON file containing flashcards (questions and answers), select a quiz mode, and proceed through an interactive quiz session. The application shows each question, accepts user input, provides immediate feedback with colored output (green for correct, red for incorrect), and maintains statistics throughout the session. At the end, users receive a summary showing their accuracy percentage and a list of terms they missed. This is particularly useful for language learning, exam preparation, or skill development.

### Key Features Implemented

The application includes several production-ready features: (1) **Dual JSON format support** - users can provide either a simple array of cards `[{"front": "...", "back": "..."}]` or a wrapped object `{"cards": [...]}`, (2) **Three quiz modes** offering different learning strategies, (3) **Case-insensitive answer matching** for better user experience, (4) **Color-coded terminal feedback** using ANSI escape sequences, (5) **Graceful error handling** with user-friendly messages, (6) **Multiple exit options** including an 'exit' command and Ctrl+C support without stack traces, and (7) **Comprehensive statistics** showing total questions, correct answers, and accuracy percentage.

---

## Architecture & Design Patterns: Strategy and Factory

### The Strategy Pattern in Quiz Modes

The application uses the Strategy design pattern to implement three different quiz delivery strategies: Sequential, Random, and Adaptive modes. Rather than embedding conditional logic in the main loop (`if mode == "sequential" then...; elif mode == "random" then...`), I created an abstract base class `QuizMode` that defines a contract with three methods: `get_next_card()` to retrieve the next card, `mark_incorrect()` to track user mistakes, and `reset()` to restart the quiz.

Each strategy inherits from `QuizMode` and implements this interface differently. `SequentialMode` serves cards in their original order from the input file. `RandomMode` shuffles the deck using Python's `random.shuffle()` and serves cards in shuffled order, with a new shuffle on reset. `AdaptiveMode` maintains a set of indices for incorrectly answered cards and rebuilds the deck on each `mark_incorrect()` call, placing incorrect cards at the front followed by shuffled correct cards. This encourages users to focus on weak areas.

### The Factory Pattern for Mode Creation

The `QuizModeFactory` class encapsulates mode instantiation. Instead of allowing callers to directly import and instantiate specific mode classes, the factory provides a single `create(mode_string, cards)` method that maps string inputs to the correct class. This provides several benefits: (1) **Loose coupling** - the main loop doesn't depend on specific mode implementations, only the factory interface, (2) **Extensibility** - adding a new mode (like `SpacedRepetitionMode`) requires only adding the class and updating the factory mapping, (3) **Error handling** - the factory validates mode names and provides helpful messages listing available modes, (4) **Case insensitivity** - the factory normalizes mode names to lowercase, improving UX.

### Why This Architecture Matters

Compared to a monolithic alternative (all logic in `main.py` with conditional branching), this design is significantly more maintainable. New developers can understand each mode by reading one class without wading through conditional logic. Tests can verify each mode independently. Adding a fourth mode doesn't touch existing code, reducing regression risk. If requirements change (e.g., "Adaptive mode should prioritize cards answered slowly, not just incorrectly"), I modify only the `AdaptiveMode` class. This separation of concerns is a cornerstone of professional software engineering and directly reduces the cost of future changes.

---

## AI Collaboration & Development Process

### How We Worked Together

I used Claude Code as my AI assistant throughout development. My approach involved clear, specific prompts that included context about requirements and constraints. For example, when building the file handler, I requested: "Support both JSON formats: array `[{"front": "...", "back": "..."}]` and object `{"cards": [...]}`. Validate structure and raise a custom error if a card is missing 'front' or 'back'. Include full Python type hints."

Claude excelled at generating clean boilerplate: the initial `load_flashcards()` function was well-structured, handled both formats correctly, and included comprehensive docstrings. The quiz engine implementation, particularly the Strategy and Factory patterns, was well-designed on the first pass with minimal changes needed.

### Guidance on Type Checking & Testing Discipline

However, I had to actively guide Claude toward production-grade type safety. When I ran `mypy --strict`, Claude's initial code had six type errors, mostly from incomplete generic type specifications (`dict` instead of `dict[str, Any]`, `list` instead of `list[Card]`). More importantly, the `run_quiz()` function used a union-type dictionary `dict[str, int | list[Card]]`, which forced callers to perform type casting. I refactored this to use separate typed variables (`total: int`, `correct: int`, `incorrect_cards: list[Card]`), which was clearer and eliminated casting.

For testing, Claude generated a solid foundation of 62 tests achieving 99% coverage. However, I had to correct two assertions that relied on exact order from probabilistic operations (random shuffling). I taught Claude to use property-based assertions ("all cards are present") instead of order-based ones ("cards appear in this sequence").

### Code Quality Standards

I enforced strict quality standards: zero Flake8 errors (PEP 8 compliance), Black formatting compliance, and Mypy strict type checking. This required fixing 9 issues total: one missing newline, three formatting inconsistencies, and five type errors. Claude understood the issues quickly and implemented fixes correctly once I explained why union types in data structures were problematic.

---

## Testing & Code Quality

I created a comprehensive test suite across three files: 20 tests for file loading (valid/invalid formats, error handling, encoding), 27 tests for quiz modes (each mode's behavior, factory pattern, interface compliance), and 15 integration tests (end-to-end quiz flows, statistics calculation, edge cases). The suite achieved 99% code coverage, well exceeding the 80% requirement.

Code quality metrics:
- **Test Coverage:** 99% (62/62 tests passing)
- **Linting:** Flake8 zero errors
- **Formatting:** Black compliant
- **Type Safety:** Mypy strict mode passed
- **Type Coverage:** 100% of public functions and classes

---

## Conclusion

This project demonstrates that AI-assisted development, when done with discipline, produces robust, production-ready code. Claude's ability to generate large amounts of correct boilerplate saved substantial time, while my responsibility for code review, type checking enforcement, test coverage verification, and architectural decisions ensured quality. The final application is maintainable, well-tested, and could be deployed immediately. Key lessons: (1) AI excels at generating initial implementations and boilerplate, (2) Strict type checking catches real bugs early, (3) Test coverage discipline (99% vs 80%) builds confidence, (4) Design patterns matter—the Strategy/Factory approach made the codebase extensible, and (5) Effective AI collaboration requires clear prompts, active code review, and knowledge of when to redirect the AI's suggestions. I will continue using this approach—leveraging AI for rapid implementation while maintaining personal responsibility for quality, testing, and architectural decisions.