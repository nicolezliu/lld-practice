"""
Test driver for the Library Management System.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import Book, BookCopy, Member, BookStatus
from search import TitleSearchStrategy, AuthorSearchStrategy, ISBNSearchStrategy
from library import Library
from datetime import datetime, timedelta


def main():
    print("=" * 60)
    print("LIBRARY MANAGEMENT — LLD PRACTICE")
    print("=" * 60)

    # --- Setup ---
    search = TitleSearchStrategy()
    lib = Library("Downtown Public Library", search)

    # Add books with copies
    book1 = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin")
    for i in range(3):
        book1.add_copy(BookCopy(f"CC-{i:03d}", book1))

    book2 = Book("978-0-20-163361-0", "Design Patterns", "Gang of Four")
    for i in range(2):
        book2.add_copy(BookCopy(f"DP-{i:03d}", book2))

    book3 = Book("978-0-13-595705-9", "The Pragmatic Programmer", "Hunt and Thomas")
    book3.add_copy(BookCopy("PP-001", book3))

    book4 = Book("978-0-59-651798-8", "Learning Python", "Mark Lutz")
    book4.add_copy(BookCopy("LP-001", book4))
    book4.add_copy(BookCopy("LP-002", book4))

    for book in [book1, book2, book3, book4]:
        lib.add_book(book)

    # Register members
    alice = Member("M001", "Alice")
    bob = Member("M002", "Bob")
    lib.register_member(alice)
    lib.register_member(bob)

    # --- Scenario 1: Search for books ---
    print("\n--- Scenario 1: Search by title ---")
    results = lib.search_books("Python")
    for book in results:
        print(f"  Found: {book.title} by {book.author} "
              f"({book.available_count}/{book.total_copies} available)")

    # --- Scenario 2: Borrow a book ---
    print("\n--- Scenario 2: Borrow a book ---")
    record = lib.borrow_book("M001", "978-0-13-468599-1")
    print(f"  Alice borrowed: {record.book_copy.book.title} "
          f"(copy {record.book_copy.copy_id})")
    print(f"  Due date: {record.due_date}")
    print(f"  Clean Code availability: "
          f"{book1.available_count}/{book1.total_copies}")

    # --- Scenario 3: Return a book ---
    print("\n--- Scenario 3: Return the book ---")
    fine = lib.return_book("M001", record.book_copy.copy_id)
    print(f"  Book returned. Fine: ${fine:.2f}")
    print(f"  Clean Code availability: "
          f"{book1.available_count}/{book1.total_copies}")

    # --- Scenario 4: Overdue book ---
    print("\n--- Scenario 4: Overdue book ---")
    past_date = datetime.now() - timedelta(days=20)
    record2 = lib.borrow_book("M002", "978-0-20-163361-0",
                               borrow_date=past_date)
    print(f"  Bob borrowed: {record2.book_copy.book.title} "
          f"(borrowed {past_date.strftime('%Y-%m-%d')})")
    print(f"  Due date: {record2.due_date.strftime('%Y-%m-%d')}")
    print(f"  Is overdue? {record2.is_overdue()}")
    print(f"  Current fine: ${record2.calculate_fine():.2f}")

    overdue = lib.get_overdue_books()
    print(f"  Total overdue books in library: {len(overdue)}")

    # Return the overdue book
    fine = lib.return_book("M002", record2.book_copy.copy_id)
    print(f"  Bob returned overdue book. Fine: ${fine:.2f}")

    # --- Scenario 5: Swap search strategy ---
    print("\n--- Scenario 5: Search by author ---")
    lib.set_search_strategy(AuthorSearchStrategy())
    results = lib.search_books("Martin")
    for book in results:
        print(f"  Found: {book.title} by {book.author}")

    # --- Scenario 6: Multiple borrows ---
    print("\n--- Scenario 6: Alice borrows multiple books ---")
    lib.set_search_strategy(TitleSearchStrategy())
    for isbn in ["978-0-13-468599-1", "978-0-20-163361-0",
                 "978-0-13-595705-9", "978-0-59-651798-8"]:
        record = lib.borrow_book("M001", isbn)
        print(f"  Borrowed: {record.book_copy.book.title}")
    print(f"  Alice's active borrows: {alice.active_borrow_count}")
    member_books = lib.get_member_books("M001")
    for r in member_books:
        print(f"    - {r.book_copy.book.title} (due {r.due_date.strftime('%Y-%m-%d')})")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens when Alice tries to borrow a 6th book?
    #   - What happens if all copies of a book are borrowed?
    #   - Try searching by ISBN
    #   - What if a suspended member tries to borrow?


if __name__ == "__main__":
    main()
