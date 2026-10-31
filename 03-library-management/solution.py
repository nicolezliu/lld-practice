"""
SOLUTION — Library Management System

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional


# ===================================================================
# Enums
# ===================================================================

class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"


class MemberStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


# ===================================================================
# Book and BookCopy
# ===================================================================

class Book:
    """
    Key design decisions:

    1. Book represents a catalog entry (metadata), not a physical item.
       Physical items are BookCopy instances. This is the "type vs instance"
       distinction — similar to Product vs InventoryItem in e-commerce.

    2. Copies are stored in a list rather than a dict because we rarely
       look up by copy_id at the Book level. The Library handles copy
       lookup across all books.
    """

    def __init__(self, isbn: str, title: str, author: str):
        self.isbn = isbn
        self.title = title
        self.author = author
        self._copies: list["BookCopy"] = []

    def add_copy(self, copy: "BookCopy") -> None:
        self._copies.append(copy)

    def get_available_copies(self) -> list["BookCopy"]:
        return [c for c in self._copies if c.status == BookStatus.AVAILABLE]

    @property
    def total_copies(self) -> int:
        return len(self._copies)

    @property
    def available_count(self) -> int:
        return len(self.get_available_copies())

    def __repr__(self) -> str:
        return f"Book({self.isbn}, '{self.title}')"


class BookCopy:
    """
    Key design decisions:

    1. Status transitions are enforced: you can only borrow an AVAILABLE
       copy and only return a BORROWED copy. This prevents invalid states.

    2. Each copy holds a reference back to its parent Book. This makes
       it easy to get book metadata from a copy without a separate lookup.
    """

    def __init__(self, copy_id: str, book: Book):
        self.copy_id = copy_id
        self.book = book
        self.status = BookStatus.AVAILABLE

    def mark_borrowed(self) -> None:
        if self.status != BookStatus.AVAILABLE:
            raise ValueError(
                f"Copy {self.copy_id} is {self.status.name}, cannot borrow"
            )
        self.status = BookStatus.BORROWED

    def mark_returned(self) -> None:
        if self.status != BookStatus.BORROWED:
            raise ValueError(
                f"Copy {self.copy_id} is {self.status.name}, cannot return"
            )
        self.status = BookStatus.AVAILABLE

    def __repr__(self) -> str:
        return f"BookCopy({self.copy_id}, {self.status.name})"


# ===================================================================
# Member
# ===================================================================

class Member:
    """
    Key design decisions:

    1. Borrow limit is a class constant (MAX_BORROW_LIMIT = 5). This
       makes it easy to change globally or override per-member subclass.

    2. Active borrows are tracked as a list of BorrowRecord references.
       An alternative would be to track only copy_ids and look up records
       from the Library — trade-off is convenience vs coupling.

    3. can_borrow() checks both status and limit in one call, so the
       Library doesn't need to know the rules.
    """

    MAX_BORROW_LIMIT = 5

    def __init__(self, member_id: str, name: str):
        self.member_id = member_id
        self.name = name
        self.status = MemberStatus.ACTIVE
        self._active_borrows: list["BorrowRecord"] = []

    def can_borrow(self) -> bool:
        return (
            self.status == MemberStatus.ACTIVE
            and len(self._active_borrows) < self.MAX_BORROW_LIMIT
        )

    def add_borrow(self, record: "BorrowRecord") -> None:
        if not self.can_borrow():
            raise ValueError(
                f"Member {self.member_id} cannot borrow "
                f"(status={self.status.name}, "
                f"borrows={len(self._active_borrows)}/{self.MAX_BORROW_LIMIT})"
            )
        self._active_borrows.append(record)

    def remove_borrow(self, record: "BorrowRecord") -> None:
        self._active_borrows.remove(record)

    @property
    def active_borrow_count(self) -> int:
        return len(self._active_borrows)

    @property
    def active_borrows(self) -> list["BorrowRecord"]:
        return list(self._active_borrows)

    def __repr__(self) -> str:
        return f"Member({self.member_id}, '{self.name}')"


# ===================================================================
# Borrow Record
# ===================================================================

class BorrowRecord:
    """
    Key design decisions:

    1. borrow_date defaults to now but can be overridden for testing.
       This is critical for writing deterministic tests with known dates.

    2. Fine calculation uses integer day difference (not fractional).
       A partial overdue day counts as a full day — this is the standard
       library convention.

    3. return_book() both records the return and calculates the fine in
       one operation, which keeps the record self-consistent.
    """

    DEFAULT_BORROW_DAYS = 14
    FINE_PER_DAY = 0.50

    def __init__(self, member: Member, book_copy: BookCopy,
                 borrow_date: Optional[datetime] = None):
        self.member = member
        self.book_copy = book_copy
        self.borrow_date = borrow_date or datetime.now()
        self.due_date = self.borrow_date + timedelta(days=self.DEFAULT_BORROW_DAYS)
        self.return_date: Optional[datetime] = None

    def return_book(self, return_date: Optional[datetime] = None) -> float:
        if self.return_date is not None:
            raise ValueError("Book has already been returned")
        self.return_date = return_date or datetime.now()
        return self.calculate_fine(as_of=self.return_date)

    def is_overdue(self, as_of: Optional[datetime] = None) -> bool:
        if self.return_date is not None:
            return False  # already returned
        check_date = as_of or datetime.now()
        return check_date > self.due_date

    def calculate_fine(self, as_of: Optional[datetime] = None) -> float:
        check_date = as_of or datetime.now()
        if check_date <= self.due_date:
            return 0.0
        overdue_days = (check_date - self.due_date).days
        return overdue_days * self.FINE_PER_DAY

    def __repr__(self) -> str:
        return (
            f"BorrowRecord(member={self.member.member_id}, "
            f"copy={self.book_copy.copy_id})"
        )


# ===================================================================
# Search strategies (Strategy pattern)
# ===================================================================

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, books: list[Book], query: str) -> list[Book]:
        ...


class TitleSearchStrategy(SearchStrategy):
    """Case-insensitive substring search on book title."""

    def search(self, books: list[Book], query: str) -> list[Book]:
        q = query.lower()
        return [b for b in books if q in b.title.lower()]


class AuthorSearchStrategy(SearchStrategy):
    """Case-insensitive substring search on author name."""

    def search(self, books: list[Book], query: str) -> list[Book]:
        q = query.lower()
        return [b for b in books if q in b.author.lower()]


class ISBNSearchStrategy(SearchStrategy):
    """Exact match on ISBN."""

    def search(self, books: list[Book], query: str) -> list[Book]:
        return [b for b in books if b.isbn == query]


# ===================================================================
# Library (the orchestrator)
# ===================================================================

class Library:
    """
    Key design decisions:

    1. Books are stored in a dict keyed by ISBN for O(1) lookup.
       Members are stored in a dict keyed by member_id.

    2. Active borrow records are stored in a list on the Library level
       (in addition to being tracked by each Member). This makes it easy
       to query all overdue books without iterating all members.

    3. borrow_book() does all validation in sequence and raises
       ValueError with descriptive messages for each failure case.
       An alternative would be to return a Result type — trade-off
       is Pythonic exceptions vs explicit error handling.

    4. The search strategy is swappable at runtime via
       set_search_strategy(). This is the classic Strategy pattern.
    """

    def __init__(self, name: str, search_strategy: SearchStrategy):
        self._name = name
        self._search_strategy = search_strategy
        self._books: dict[str, Book] = {}          # ISBN → Book
        self._members: dict[str, Member] = {}      # member_id → Member
        self._active_records: list[BorrowRecord] = []
        self._all_records: list[BorrowRecord] = []  # historical

    def add_book(self, book: Book) -> None:
        if book.isbn in self._books:
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self._books[book.isbn] = book

    def register_member(self, member: Member) -> None:
        if member.member_id in self._members:
            raise ValueError(
                f"Member with ID {member.member_id} already exists"
            )
        self._members[member.member_id] = member

    def search_books(self, query: str) -> list[Book]:
        catalog = list(self._books.values())
        return self._search_strategy.search(catalog, query)

    def borrow_book(self, member_id: str, isbn: str,
                    borrow_date: Optional[datetime] = None) -> BorrowRecord:
        # 1. Find the member
        member = self._members.get(member_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")

        # 2. Check member can borrow
        if not member.can_borrow():
            raise ValueError(
                f"Member {member_id} cannot borrow "
                f"(status={member.status.name}, "
                f"borrows={member.active_borrow_count}/"
                f"{member.MAX_BORROW_LIMIT})"
            )

        # 3. Find the book
        book = self._books.get(isbn)
        if book is None:
            raise ValueError(f"Book with ISBN {isbn} not found")

        # 4. Find an available copy
        available = book.get_available_copies()
        if not available:
            raise ValueError(
                f"No available copies of '{book.title}' (ISBN: {isbn})"
            )
        copy = available[0]

        # 5. Mark the copy as borrowed
        copy.mark_borrowed()

        # 6. Create a BorrowRecord
        record = BorrowRecord(member, copy, borrow_date=borrow_date)

        # 7. Add the record to the member
        member.add_borrow(record)

        # 8. Store the record
        self._active_records.append(record)
        self._all_records.append(record)

        return record

    def return_book(self, member_id: str, copy_id: str,
                    return_date: Optional[datetime] = None) -> float:
        # Find the active borrow record for this member and copy
        record = None
        for r in self._active_records:
            if (r.member.member_id == member_id
                    and r.book_copy.copy_id == copy_id):
                record = r
                break

        if record is None:
            raise ValueError(
                f"No active borrow found for member {member_id}, "
                f"copy {copy_id}"
            )

        # Mark the copy as returned
        record.book_copy.mark_returned()

        # Calculate fine and record return
        fine = record.return_book(return_date=return_date)

        # Remove from member's active borrows
        record.member.remove_borrow(record)

        # Remove from active records
        self._active_records.remove(record)

        return fine

    def get_overdue_books(self,
                         as_of: Optional[datetime] = None) -> list[BorrowRecord]:
        return [r for r in self._active_records if r.is_overdue(as_of=as_of)]

    def get_member_books(self, member_id: str) -> list[BorrowRecord]:
        member = self._members.get(member_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")
        return member.active_borrows

    def set_search_strategy(self, strategy: SearchStrategy) -> None:
        self._search_strategy = strategy
