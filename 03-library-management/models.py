"""
Models for the Library Management System.

Your job: fill in the class bodies.
- Think about the relationship between Book and BookCopy (a Book HAS many copies)
- Think about what state a BookCopy tracks vs what a BorrowRecord tracks
- Think about how Member enforces borrow limits
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BookStatus(Enum):
    """Status of an individual book copy."""
    # TODO: define members (AVAILABLE, BORROWED, RESERVED)
    pass


class MemberStatus(Enum):
    """Status of a library member."""
    # TODO: define members (ACTIVE, SUSPENDED)
    pass


# ---------------------------------------------------------------------------
# Book and BookCopy
# ---------------------------------------------------------------------------

class Book:
    """
    Represents a book title in the catalog (not a physical copy).

    Think about:
    - A Book has metadata (ISBN, title, author)
    - A Book can have multiple physical copies (BookCopy instances)
    - How do you add/remove copies?
    - How do you check how many copies are available?
    """

    def __init__(self, isbn: str, title: str, author: str):
        """
        Initialize a book in the catalog.

        Args:
            isbn: unique ISBN identifier
            title: book title
            author: book author
        """
        # TODO: store isbn, title, author
        # TODO: initialize an empty list/dict of copies
        pass

    def add_copy(self, copy: "BookCopy") -> None:
        """Add a physical copy of this book."""
        # TODO
        pass

    def get_available_copies(self) -> list["BookCopy"]:
        """Return a list of copies that are currently AVAILABLE."""
        # TODO
        pass

    @property
    def total_copies(self) -> int:
        """Return the total number of copies (all statuses)."""
        # TODO
        pass

    @property
    def available_count(self) -> int:
        """Return the number of available copies."""
        # TODO
        pass

    def __repr__(self) -> str:
        return f"Book({self.isbn}, '{self.title}')"


class BookCopy:
    """
    A single physical copy of a book.

    Think about:
    - Each copy has a unique copy_id
    - Each copy has a status (AVAILABLE, BORROWED, RESERVED)
    - Each copy references the parent Book
    """

    def __init__(self, copy_id: str, book: Book):
        """
        Args:
            copy_id: unique identifier for this copy
            book: the Book this is a copy of
        """
        # TODO: store copy_id, book reference, initial status (AVAILABLE)
        pass

    def mark_borrowed(self) -> None:
        """
        Mark this copy as borrowed.
        Raise ValueError if not currently AVAILABLE.
        """
        # TODO
        pass

    def mark_returned(self) -> None:
        """
        Mark this copy as available (returned).
        Raise ValueError if not currently BORROWED.
        """
        # TODO
        pass

    def __repr__(self) -> str:
        return f"BookCopy({self.copy_id}, {self.status.name})"


# ---------------------------------------------------------------------------
# Member
# ---------------------------------------------------------------------------

class Member:
    """
    A library member who can borrow books.

    Think about:
    - What identifies a member? (member_id, name)
    - How do you track which books they have borrowed?
    - How do you enforce a borrow limit (max 5)?
    - What does it mean for a member to be SUSPENDED?
    """

    MAX_BORROW_LIMIT = 5

    def __init__(self, member_id: str, name: str):
        """
        Args:
            member_id: unique member identifier
            name: member's name
        """
        # TODO: store member_id, name, status (ACTIVE)
        # TODO: initialize an empty list of active borrows
        pass

    def can_borrow(self) -> bool:
        """
        Return True if this member can borrow another book.

        A member can borrow if:
        - They are ACTIVE (not SUSPENDED)
        - They have fewer than MAX_BORROW_LIMIT active borrows
        """
        # TODO
        pass

    def add_borrow(self, record: "BorrowRecord") -> None:
        """
        Add a borrow record to this member's active borrows.
        Raise ValueError if the member cannot borrow.
        """
        # TODO
        pass

    def remove_borrow(self, record: "BorrowRecord") -> None:
        """Remove a borrow record when a book is returned."""
        # TODO
        pass

    @property
    def active_borrow_count(self) -> int:
        """Return the number of books currently borrowed."""
        # TODO
        pass

    def __repr__(self) -> str:
        return f"Member({self.member_id}, '{self.name}')"


# ---------------------------------------------------------------------------
# Borrow Record
# ---------------------------------------------------------------------------

class BorrowRecord:
    """
    Tracks a single borrow transaction.

    Think about:
    - Which member borrowed which copy?
    - When was it borrowed? When is it due?
    - When was it returned (None if still out)?
    - How do you calculate overdue fines?
    """

    DEFAULT_BORROW_DAYS = 14
    FINE_PER_DAY = 0.50

    def __init__(self, member: Member, book_copy: BookCopy,
                 borrow_date: Optional[datetime] = None):
        """
        Args:
            member: the member borrowing the book
            book_copy: the physical copy being borrowed
            borrow_date: when the book was borrowed (defaults to now)
        """
        # TODO: store member, book_copy, borrow_date, due_date, return_date
        # due_date = borrow_date + DEFAULT_BORROW_DAYS
        # return_date starts as None
        pass

    def return_book(self, return_date: Optional[datetime] = None) -> float:
        """
        Mark this borrow as returned and calculate any overdue fine.

        Args:
            return_date: when the book was returned (defaults to now)

        Returns:
            The fine amount ($0.00 if not overdue).

        Raises:
            ValueError: if already returned.
        """
        # TODO
        pass

    def is_overdue(self, as_of: Optional[datetime] = None) -> bool:
        """
        Check if this borrow is overdue.

        Args:
            as_of: the date to check against (defaults to now)
        """
        # TODO
        pass

    def calculate_fine(self, as_of: Optional[datetime] = None) -> float:
        """
        Calculate the overdue fine.

        Args:
            as_of: the date to calculate fine up to (defaults to now)

        Returns:
            Fine amount: $0.50 per overdue day, $0.00 if not overdue.
        """
        # TODO
        pass

    def __repr__(self) -> str:
        return (
            f"BorrowRecord(member={self.member.member_id}, "
            f"copy={self.book_copy.copy_id})"
        )
