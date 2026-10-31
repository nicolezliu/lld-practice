"""
Core Library logic.

Your job: implement the Library class.
This is the main entry point — it orchestrates books, members, and borrowing.

Think about:
- How do you register books and members?
- How do you handle borrowing (find available copy, create record, update statuses)?
- How do you handle returns (find record, calculate fine, update statuses)?
- How do you find overdue books?
"""

from typing import Optional
from datetime import datetime
from models import Book, BookCopy, Member, BorrowRecord, BookStatus
from search import SearchStrategy


class Library:
    """
    The main library system.

    Manages the catalog, members, and borrow records.
    """

    def __init__(self, name: str, search_strategy: SearchStrategy):
        """
        Initialize the library.

        Args:
            name: name of the library
            search_strategy: the search strategy to use for finding books
        """
        # TODO: store name, search strategy
        # TODO: initialize collections for books, members, borrow records
        pass

    def add_book(self, book: Book) -> None:
        """
        Add a book to the catalog.

        Raise ValueError if a book with the same ISBN already exists.
        """
        # TODO
        pass

    def register_member(self, member: Member) -> None:
        """
        Register a new member.

        Raise ValueError if a member with the same ID already exists.
        """
        # TODO
        pass

    def search_books(self, query: str) -> list[Book]:
        """
        Search the catalog using the configured search strategy.

        Returns:
            A list of matching books.
        """
        # TODO: delegate to the search strategy
        pass

    def borrow_book(self, member_id: str, isbn: str,
                    borrow_date: Optional[datetime] = None) -> BorrowRecord:
        """
        Borrow a book copy.

        Steps:
        1. Find the member (raise ValueError if not found)
        2. Check member can borrow (raise ValueError if not)
        3. Find the book (raise ValueError if not found)
        4. Find an available copy (raise ValueError if none)
        5. Mark the copy as borrowed
        6. Create a BorrowRecord
        7. Add the record to the member's active borrows
        8. Store the record

        Returns:
            The BorrowRecord for this transaction.
        """
        # TODO
        pass

    def return_book(self, member_id: str, copy_id: str,
                    return_date: Optional[datetime] = None) -> float:
        """
        Return a borrowed book.

        Steps:
        1. Find the active borrow record for this member and copy
        2. Mark the copy as returned
        3. Calculate any overdue fine
        4. Remove the record from the member's active borrows
        5. Store the return date on the record

        Returns:
            The fine amount ($0.00 if not overdue).

        Raises:
            ValueError: if no matching active borrow is found.
        """
        # TODO
        pass

    def get_overdue_books(self,
                         as_of: Optional[datetime] = None) -> list[BorrowRecord]:
        """
        Return a list of all currently overdue borrow records.

        Args:
            as_of: the date to check against (defaults to now)
        """
        # TODO
        pass

    def get_member_books(self, member_id: str) -> list[BorrowRecord]:
        """
        Return all active borrow records for a member.

        Raises:
            ValueError: if member not found.
        """
        # TODO
        pass

    def set_search_strategy(self, strategy: SearchStrategy) -> None:
        """Swap the search strategy at runtime."""
        # TODO
        pass
