# Library Management System — LLD Practice

## Problem Statement
Design a library management system that handles books, members, borrowing, and returns.

## Requirements

### Functional
- The library has books identified by ISBN, with title, author, and multiple copies
- Each physical copy of a book is tracked individually (status: available, borrowed, reserved)
- Members can search for books by title, author, or ISBN
- Members can borrow available book copies (max 5 books at a time)
- Members can return borrowed books
- Each borrow has a due date (14 days from borrow date by default)
- Overdue books incur a fine of $0.50 per day

### Non-Functional
- Efficient search across large catalogs
- Extensible search strategies (easy to add new search criteria)
- Clean separation between domain models and library operations

## Suggested Design Patterns
- **Strategy** — for search (search by title, author, ISBN — swap algorithms)
- **Observer** — for due date notifications (stretch goal)
- **Factory** — for creating entities (books, members, records)

## Your Task
1. Fill in the class bodies in `models.py`
2. Implement the search strategies in `search.py`
3. Implement the library logic in `library.py`
4. Run `main.py` to test your design end-to-end
5. Add your own test scenarios in `main.py`

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, Book, BookCopy, Member, BorrowRecord
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Search strategies
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: Library integration (borrow, return, overdue, search)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add a `DueDateObserver` that gets notified when a book becomes overdue
- Add a reservation system (members can reserve books that are currently borrowed)
- Add member suspension (auto-suspend after too many overdue returns)
- Add category/genre-based search
