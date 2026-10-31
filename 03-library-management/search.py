"""
Search strategies for the Library.

Your job: implement the Strategy pattern for searching books.
- Define an abstract SearchStrategy
- Implement concrete strategies for title, author, and ISBN search
- Think about: how would you add a genre-based search without modifying existing code?
"""

from abc import ABC, abstractmethod
from models import Book


class SearchStrategy(ABC):
    """Abstract search strategy — finds books matching a query."""

    @abstractmethod
    def search(self, books: list[Book], query: str) -> list[Book]:
        """
        Search a list of books using this strategy.

        Args:
            books: the catalog of books to search
            query: the search query string

        Returns:
            A list of books matching the query (case-insensitive).
        """
        ...


class TitleSearchStrategy(SearchStrategy):
    """
    Search books by title.

    Matches if the query appears anywhere in the book's title (case-insensitive).
    Example: query="python" matches "Learning Python" and "Python Cookbook"
    """

    def search(self, books: list[Book], query: str) -> list[Book]:
        # TODO: filter books where query is a substring of title
        pass


class AuthorSearchStrategy(SearchStrategy):
    """
    Search books by author name.

    Matches if the query appears anywhere in the author's name (case-insensitive).
    Example: query="martin" matches books by "Robert C. Martin"
    """

    def search(self, books: list[Book], query: str) -> list[Book]:
        # TODO: filter books where query is a substring of author
        pass


class ISBNSearchStrategy(SearchStrategy):
    """
    Search books by ISBN.

    Matches if the query exactly equals the book's ISBN.
    Example: query="978-0-13-468599-1" matches exactly one book
    """

    def search(self, books: list[Book], query: str) -> list[Book]:
        # TODO: filter books where ISBN matches exactly
        pass


# STRETCH: Add a GenreSearchStrategy, CombinedSearchStrategy (searches multiple fields), etc.
