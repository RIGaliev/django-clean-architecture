from collections.abc import Sequence
from datetime import UTC, datetime
from typing import NoReturn

from django.db import DatabaseError, IntegrityError

from library.adapters.database.tables import BookTable
from library.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    LibraryException,
)
from library.domains.entities.book import (
    Book,
    BookId,
    BookPaginationParams,
    CreateBook,
    UpdateBook,
)
from library.domains.interfaces.storages.book import IBookStorage


class BookStorage(IBookStorage):
    def fetch_book_by_id(self, *, book_id: BookId) -> Book | None:
        book = BookTable.objects.filter(id=book_id, deleted_at__isnull=True).first()

        if book is None:
            return None

        return Book(
            id=BookId(book.id),
            title=book.title,
            year=book.year,
            author=book.author,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

    def exists_book_by_id(self, *, book_id: BookId) -> bool:
        return BookTable.objects.filter(id=book_id, deleted_at__isnull=True).exists()

    def count_books(self, *, params: BookPaginationParams) -> int:
        return BookTable.objects.filter(deleted_at__isnull=True)[
            params.offset : params.offset + params.limit
        ].count()

    def fetch_book_list(self, *, params: BookPaginationParams) -> Sequence[Book]:
        result = BookTable.objects.filter(deleted_at__isnull=True).order_by("id")[
            params.offset : params.offset + params.limit
        ]
        return [
            Book(
                id=book.id,
                title=book.title,
                year=book.year,
                author=book.author,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            for book in result
        ]

    def create_book(self, *, book: CreateBook) -> Book:
        try:
            result = BookTable.objects.create(
                title=book.title,
                year=book.year,
                author=book.author,
            )
        except IntegrityError as e:
            self._raise_error(e)
        return Book(
            id=BookId(result.id),
            title=result.title,
            year=result.year,
            author=result.author,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    def delete_book_by_id(self, *, book_id: BookId) -> None:
        BookTable.objects.filter(id=book_id).update(deleted_at=datetime.now(tz=UTC))

    def update_book_by_id(self, *, update_book: UpdateBook) -> Book:
        try:
            BookTable.objects.filter(id=update_book.id).update(**update_book.to_dict())
            result = BookTable.objects.get(id=update_book.id)
        except BookTable.DoesNotExist as e:
            raise EntityNotFoundException(entity=Book, entity_id=update_book.id) from e
        except IntegrityError as e:
            self._raise_error(e)
        return Book(
            id=BookId(result.id),
            title=result.title,
            year=result.year,
            author=result.author,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    def _raise_error(self, e: DatabaseError) -> NoReturn:
        constraint = e.__cause__.diag.constraint_name
        if constraint == "ix__books__title_year_author":
            raise EntityAlreadyExistsException("Book already exists") from e
        raise LibraryException(message="Unknown error") from e
