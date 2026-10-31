"""
Phased tests for the Library Management System.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Search only
    python -m pytest tests.py -v -k "phase3"    # Library integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest
from datetime import datetime, timedelta

from models import (
    BookStatus, MemberStatus,
    Book, BookCopy, Member, BorrowRecord,
)
from search import TitleSearchStrategy, AuthorSearchStrategy, ISBNSearchStrategy
from library import Library


# ===================================================================
# PHASE 1: Models — Enums, Book, BookCopy, Member, BorrowRecord
# ===================================================================

class TestPhase1Enums:
    """Verify enums have the right members."""

    def test_book_statuses_exist(self):
        assert BookStatus.AVAILABLE
        assert BookStatus.BORROWED
        assert BookStatus.RESERVED

    def test_member_statuses_exist(self):
        assert MemberStatus.ACTIVE
        assert MemberStatus.SUSPENDED


class TestPhase1Book:
    """Verify Book catalog entry behavior."""

    def test_book_creation(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        assert book.isbn == "978-0-13-468599-1"
        assert book.title == "Clean Code"
        assert book.author == "Robert C. Martin"

    def test_book_starts_with_no_copies(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        assert book.total_copies == 0
        assert book.available_count == 0

    def test_add_copy(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        book.add_copy(copy)
        assert book.total_copies == 1
        assert book.available_count == 1

    def test_multiple_copies(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        book.add_copy(BookCopy("CC-001", book))
        book.add_copy(BookCopy("CC-002", book))
        book.add_copy(BookCopy("CC-003", book))
        assert book.total_copies == 3
        assert book.available_count == 3

    def test_available_copies_excludes_borrowed(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        c1 = BookCopy("CC-001", book)
        c2 = BookCopy("CC-002", book)
        book.add_copy(c1)
        book.add_copy(c2)
        c1.mark_borrowed()
        assert book.available_count == 1
        available = book.get_available_copies()
        assert len(available) == 1
        assert available[0] is c2


class TestPhase1BookCopy:
    """Verify BookCopy status transitions."""

    def test_new_copy_is_available(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        assert copy.status == BookStatus.AVAILABLE

    def test_mark_borrowed(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        copy.mark_borrowed()
        assert copy.status == BookStatus.BORROWED

    def test_mark_returned(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        copy.mark_borrowed()
        copy.mark_returned()
        assert copy.status == BookStatus.AVAILABLE

    def test_borrow_unavailable_raises(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        copy.mark_borrowed()
        with pytest.raises(ValueError):
            copy.mark_borrowed()

    def test_return_available_raises(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        with pytest.raises(ValueError):
            copy.mark_returned()

    def test_copy_references_book(self):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        assert copy.book is book


class TestPhase1Member:
    """Verify Member behavior and borrow limits."""

    def test_member_creation(self):
        member = Member("M001", "Alice")
        assert member.member_id == "M001"
        assert member.name == "Alice"
        assert member.status == MemberStatus.ACTIVE

    def test_member_can_borrow_initially(self):
        member = Member("M001", "Alice")
        assert member.can_borrow() is True

    def test_member_active_borrow_count(self):
        member = Member("M001", "Alice")
        assert member.active_borrow_count == 0

    def test_suspended_member_cannot_borrow(self):
        member = Member("M001", "Alice")
        member.status = MemberStatus.SUSPENDED
        assert member.can_borrow() is False


class TestPhase1BorrowRecord:
    """Verify BorrowRecord creation and fine calculation."""

    def _make_record(self, borrow_date=None):
        book = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
        copy = BookCopy("CC-001", book)
        member = Member("M001", "Alice")
        return BorrowRecord(member, copy, borrow_date=borrow_date)

    def test_record_creation(self):
        now = datetime(2024, 1, 1, 10, 0)
        record = self._make_record(borrow_date=now)
        assert record.member.member_id == "M001"
        assert record.book_copy.copy_id == "CC-001"
        assert record.borrow_date == now
        assert record.due_date == now + timedelta(days=14)
        assert record.return_date is None

    def test_not_overdue_before_due_date(self):
        borrow = datetime(2024, 1, 1)
        record = self._make_record(borrow_date=borrow)
        check = datetime(2024, 1, 10)  # 9 days later, due in 14
        assert record.is_overdue(as_of=check) is False

    def test_overdue_after_due_date(self):
        borrow = datetime(2024, 1, 1)
        record = self._make_record(borrow_date=borrow)
        check = datetime(2024, 1, 20)  # 19 days later, due was at 14
        assert record.is_overdue(as_of=check) is True

    def test_fine_when_overdue(self):
        borrow = datetime(2024, 1, 1)
        record = self._make_record(borrow_date=borrow)
        # 5 days overdue: due Jan 15, check Jan 20
        check = datetime(2024, 1, 20)
        fine = record.calculate_fine(as_of=check)
        assert fine == 2.50  # 5 days * $0.50

    def test_no_fine_when_not_overdue(self):
        borrow = datetime(2024, 1, 1)
        record = self._make_record(borrow_date=borrow)
        check = datetime(2024, 1, 10)
        fine = record.calculate_fine(as_of=check)
        assert fine == 0.0

    def test_return_book_records_date(self):
        borrow = datetime(2024, 1, 1)
        record = self._make_record(borrow_date=borrow)
        return_dt = datetime(2024, 1, 10)
        record.return_book(return_date=return_dt)
        assert record.return_date == return_dt

    def test_return_already_returned_raises(self):
        record = self._make_record(borrow_date=datetime(2024, 1, 1))
        record.return_book(return_date=datetime(2024, 1, 10))
        with pytest.raises(ValueError):
            record.return_book(return_date=datetime(2024, 1, 12))


# ===================================================================
# PHASE 2: Search Strategies
# ===================================================================

class TestPhase2TitleSearch:
    """Verify title-based search."""

    def _make_catalog(self) -> list[Book]:
        return [
            Book("ISBN-1", "Clean Code", "Robert C. Martin"),
            Book("ISBN-2", "Clean Architecture", "Robert C. Martin"),
            Book("ISBN-3", "Design Patterns", "Gang of Four"),
            Book("ISBN-4", "The Pragmatic Programmer", "Hunt and Thomas"),
        ]

    def test_finds_matching_title(self):
        strategy = TitleSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "Clean")
        assert len(results) == 2

    def test_case_insensitive(self):
        strategy = TitleSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "clean")
        assert len(results) == 2

    def test_no_match_returns_empty(self):
        strategy = TitleSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "Nonexistent")
        assert len(results) == 0

    def test_partial_match(self):
        strategy = TitleSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "Prag")
        assert len(results) == 1
        assert results[0].title == "The Pragmatic Programmer"


class TestPhase2AuthorSearch:
    """Verify author-based search."""

    def _make_catalog(self) -> list[Book]:
        return [
            Book("ISBN-1", "Clean Code", "Robert C. Martin"),
            Book("ISBN-2", "Clean Architecture", "Robert C. Martin"),
            Book("ISBN-3", "Design Patterns", "Gang of Four"),
        ]

    def test_finds_by_author(self):
        strategy = AuthorSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "Martin")
        assert len(results) == 2

    def test_case_insensitive(self):
        strategy = AuthorSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "martin")
        assert len(results) == 2

    def test_no_match(self):
        strategy = AuthorSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "Fowler")
        assert len(results) == 0


class TestPhase2ISBNSearch:
    """Verify ISBN-based search."""

    def _make_catalog(self) -> list[Book]:
        return [
            Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin"),
            Book("978-0-20-163361-0", "Design Patterns", "Gang of Four"),
        ]

    def test_exact_isbn_match(self):
        strategy = ISBNSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "978-0-13-468599-1")
        assert len(results) == 1
        assert results[0].title == "Clean Code"

    def test_no_partial_isbn_match(self):
        strategy = ISBNSearchStrategy()
        books = self._make_catalog()
        results = strategy.search(books, "978")
        assert len(results) == 0


# ===================================================================
# PHASE 3: Library Integration
# ===================================================================

class TestPhase3Library:
    """Full integration tests for the Library."""

    def _make_library(self) -> Library:
        lib = Library("Test Library", TitleSearchStrategy())

        # Add books with copies
        book1 = Book("ISBN-1", "Clean Code", "Robert C. Martin")
        c1 = BookCopy("CC-001", book1)
        c2 = BookCopy("CC-002", book1)
        book1.add_copy(c1)
        book1.add_copy(c2)

        book2 = Book("ISBN-2", "Design Patterns", "Gang of Four")
        c3 = BookCopy("DP-001", book2)
        book2.add_copy(c3)

        book3 = Book("ISBN-3", "The Pragmatic Programmer", "Hunt and Thomas")
        c4 = BookCopy("PP-001", book3)
        book3.add_copy(c4)

        lib.add_book(book1)
        lib.add_book(book2)
        lib.add_book(book3)

        # Add members
        lib.register_member(Member("M001", "Alice"))
        lib.register_member(Member("M002", "Bob"))

        return lib

    def test_add_duplicate_book_raises(self):
        lib = self._make_library()
        with pytest.raises(ValueError):
            lib.add_book(Book("ISBN-1", "Duplicate", "Author"))

    def test_register_duplicate_member_raises(self):
        lib = self._make_library()
        with pytest.raises(ValueError):
            lib.register_member(Member("M001", "Alice Clone"))

    def test_borrow_book_success(self):
        lib = self._make_library()
        record = lib.borrow_book("M001", "ISBN-1")
        assert record is not None
        assert record.member.member_id == "M001"
        assert record.book_copy.book.isbn == "ISBN-1"
        assert record.book_copy.status == BookStatus.BORROWED

    def test_borrow_reduces_availability(self):
        lib = self._make_library()
        lib.borrow_book("M001", "ISBN-1")
        # ISBN-1 had 2 copies, now 1 should be available
        results = lib.search_books("Clean Code")
        assert len(results) == 1
        assert results[0].available_count == 1

    def test_borrow_nonexistent_member_raises(self):
        lib = self._make_library()
        with pytest.raises(ValueError):
            lib.borrow_book("M999", "ISBN-1")

    def test_borrow_nonexistent_book_raises(self):
        lib = self._make_library()
        with pytest.raises(ValueError):
            lib.borrow_book("M001", "ISBN-999")

    def test_borrow_no_copies_available_raises(self):
        lib = self._make_library()
        # ISBN-2 has only 1 copy
        lib.borrow_book("M001", "ISBN-2")
        with pytest.raises(ValueError):
            lib.borrow_book("M002", "ISBN-2")

    def test_return_book_success(self):
        lib = self._make_library()
        record = lib.borrow_book("M001", "ISBN-1")
        copy_id = record.book_copy.copy_id
        fine = lib.return_book("M001", copy_id)
        assert fine == 0.0  # returned immediately, no overdue
        assert record.book_copy.status == BookStatus.AVAILABLE

    def test_return_with_overdue_fine(self):
        lib = self._make_library()
        borrow_date = datetime(2024, 1, 1)
        record = lib.borrow_book("M001", "ISBN-1", borrow_date=borrow_date)
        copy_id = record.book_copy.copy_id
        # Return 5 days late (due Jan 15, return Jan 20)
        return_date = datetime(2024, 1, 20)
        fine = lib.return_book("M001", copy_id, return_date=return_date)
        assert fine == 2.50  # 5 days * $0.50

    def test_return_unknown_borrow_raises(self):
        lib = self._make_library()
        with pytest.raises(ValueError):
            lib.return_book("M001", "GHOST-COPY")

    def test_get_overdue_books(self):
        lib = self._make_library()
        borrow_date = datetime(2024, 1, 1)
        lib.borrow_book("M001", "ISBN-1", borrow_date=borrow_date)
        lib.borrow_book("M002", "ISBN-2", borrow_date=borrow_date)
        # Check 20 days later — both should be overdue
        check_date = datetime(2024, 1, 25)
        overdue = lib.get_overdue_books(as_of=check_date)
        assert len(overdue) == 2

    def test_search_with_strategy_swap(self):
        lib = self._make_library()
        # Default is TitleSearchStrategy
        results = lib.search_books("Clean")
        assert len(results) == 1

        # Swap to AuthorSearchStrategy
        lib.set_search_strategy(AuthorSearchStrategy())
        results = lib.search_books("Martin")
        assert len(results) == 1
        assert results[0].title == "Clean Code"

    def test_member_borrow_limit(self):
        lib = Library("Limit Test", TitleSearchStrategy())
        member = Member("M001", "Alice")
        lib.register_member(member)

        # Add 6 different books with 1 copy each
        for i in range(6):
            book = Book(f"ISBN-{i}", f"Book {i}", f"Author {i}")
            copy = BookCopy(f"COPY-{i}", book)
            book.add_copy(copy)
            lib.add_book(book)

        # Borrow 5 should succeed
        for i in range(5):
            lib.borrow_book("M001", f"ISBN-{i}")

        # 6th borrow should fail
        with pytest.raises(ValueError):
            lib.borrow_book("M001", "ISBN-5")

    def test_get_member_books(self):
        lib = self._make_library()
        lib.borrow_book("M001", "ISBN-1")
        lib.borrow_book("M001", "ISBN-2")
        records = lib.get_member_books("M001")
        assert len(records) == 2
