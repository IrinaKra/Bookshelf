```mermaid
classDiagram
  class Book {
    +title: str
    +author: str
    +category: str
    +isbn: str
  }
  class Shelf {
    +name: str
    -books: List~Book~
    +add_books(books: List~Book~): void
    +sort_books_by_title(): void
    +categories(): Set~str~
  }
  class Room {
    +owner: str
    -shelves: List~Shelf~
    +add_shelf(shelf: Shelf): void
  }
  class Catalog {
    -room: Room
    +organize_books_by_category(pile: Set~Book~): void
    +sort_books_on_all_shelves(): void
    +dump(): str
  }
  Room "1" *-- "many" Shelf
  Shelf "1" o-- "many" Book
  Catalog "1" --> "1" Room
```
