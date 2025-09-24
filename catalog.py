from dataclasses import dataclass, field
from typing import List, Dict, Iterable, Optional
import pandas as pd


@dataclass(frozen=True)
class Book:
    """
    Book. Frozen -> hashable -> can be placed into a set.
    """
    id: str
    title: str
    author: str
    category: str
    isbn: Optional[str] = None


@dataclass
class Shelf:
    """
    Shelf: one shelf can contain multiple categories,
    but books of the same category must always be on the same shelf.
    """
    name: str
    books: List[Book] = field(default_factory=list)

    def add_books(self, books: Iterable[Book]) -> None:
        self.books.extend(books)

    def sort_books_by_title(self) -> None:
        """Sort by title in ascending order"""
        self.books.sort(key=lambda b: b.title.casefold())

    def categories(self) -> set[str]:
        return {b.category for b in self.books}

    def __str__(self) -> str:
        cats = ", ".join(sorted(self.categories())) or "-"
        lines = [f"Shelf '{self.name}' ({len(self.books)} books; categories: {cats})"]
        for b in self.books:
            lines.append(f"  - {b.title} — {b.author} [{b.category}] (id={b.id})")
        return "\n".join(lines)


@dataclass
class Room:
    """Room is a collection of shelves."""
    owner: str
    shelves: List[Shelf] = field(default_factory=list)

    def add_shelf(self, shelf: Shelf) -> None:
        self.shelves.append(shelf)


class Catalog:
    """
    Digital catalog: can distribute a 'pile' of books across shelves so that
      * all books of the same category end up on the same shelf;
      * a shelf may contain multiple categories;
      * then sort books on each shelf by title.
    """
    def __init__(self, room: Room):
        self.room = room

    # STEP 1: place books by categories -> shelves
    def organize_books_by_category(self, pile: Iterable[Book]) -> None:
        if not self.room.shelves:
            raise ValueError("No shelves in the room.")

        # Group books by category
        by_cat: Dict[str, List[Book]] = {}
        for b in pile:
            by_cat.setdefault(b.category, []).append(b)

        # Determine category order (stable/deterministic)
        categories = sorted(by_cat.keys(), key=str.lower)

        # Clear shelves before a new placement
        for sh in self.room.shelves:
            sh.books.clear()

        # Round-robin: category 0 -> shelf 0, category 1 -> shelf 1, ..., category k -> shelf k % n
        n = len(self.room.shelves)
        for i, cat in enumerate(categories):
            shelf = self.room.shelves[i % n]
            shelf.add_books(by_cat[cat])

    # STEP 2: walk all shelves and sort books by title
    def sort_books_on_all_shelves(self) -> None:
        for shelf in self.room.shelves:
            shelf.sort_books_by_title()

    def dump(self) -> str:
        return "\n\n".join(str(s) for s in self.room.shelves)

    def verify_constraint_same_category_same_shelf(self) -> None:
        """
        Verify that each category appears on at most one shelf.
        Raises AssertionError if the invariant is broken.
        """
        seen: Dict[str, str] = {}
        for shelf in self.room.shelves:
            for cat in shelf.categories():
                if cat in seen and seen[cat] != shelf.name:
                    raise AssertionError(
                        f"Category '{cat}' was found on shelves '{seen[cat]}' and '{shelf.name}'"
                    )
                seen[cat] = shelf.name

    def to_dataframe(self):
        """
        Return a pandas.DataFrame with columns: id, title, author, category, isbn, shelf_name.
        """
        rows = []
        for shelf in self.room.shelves:
            for b in shelf.books:
                rows.append(
                    {
                        "id": b.id,
                        "title": b.title,
                        "author": b.author,
                        "category": b.category,
                        "isbn": b.isbn,
                        "shelf_name": shelf.name,
                    }
                )
        return pd.DataFrame(rows)


def demo():
    # 1) Bob's room with a collection of shelves
    room = Room(owner="Bob", shelves=[Shelf("Left"), Shelf("Right"), Shelf("Top")])

    # 2) start with a list of books
    pile: List[Book] = [
        Book("b001", "A Tale of Two Cities", "Charles Dickens", "Classic"),
        Book("b002", "Brave New World", "Aldous Huxley", "Dystopian"),
        Book("b003", "The Pragmatic Programmer", "Andrew Hunt", "Programming"),
        Book("b004", "Clean Code", "Robert C. Martin", "Programming"),
        Book("b005", "Do Androids Dream of Electric Sheep?", "Philip K. Dick", "Sci-Fi"),
        Book("b006", "I, Robot", "Isaac Asimov", "Sci-Fi"),
        Book("b007", "The Name of the Rose", "Umberto Eco", "Mystery"),
    ]

    catalog = Catalog(room)

    # STEP 1: place by categories (same category -> same shelf; a shelf may hold several categories)
    catalog.organize_books_by_category(pile)

    # STEP 2: sort books by title on every shelf
    catalog.sort_books_on_all_shelves()

    # Verify invariant
    catalog.verify_constraint_same_category_same_shelf()

    # Print result
    print(catalog.dump())

    try:
        df = catalog.to_dataframe()
        print("\nDataFrame preview:")
        print(df.head())

        # Example of a per-shelf × category pivot using pandas
        pivot = df.pivot_table(index="shelf_name", columns="category", values="title", aggfunc="count", fill_value=0)
        print("\nPivot (counts per shelf × category):")
        print(pivot)
    except RuntimeError:
        pass 


if __name__ == "__main__":
    demo()
