from django.db.models import CharField, IntegerField, UniqueConstraint

from library.adapters.database.base import (
    BaseTable,
    IdentifiableMixin,
    TimestampedMixin,
)


class BookTable(BaseTable, TimestampedMixin, IdentifiableMixin):
    title = CharField(max_length=255)
    year = IntegerField()
    author = CharField(max_length=255)

    class Meta:
        db_table = "book"
        constraints = [
            UniqueConstraint(
                fields=["title", "year", "author"],
                name="ix__books__title_year_author",
            ),
        ]

    def __str__(self) -> str:
        return self.title


class UserTable(BaseTable, TimestampedMixin, IdentifiableMixin):
    username = CharField(max_length=255)
    email = CharField(max_length=255)

    class Meta:
        db_table = "user"
        constraints = [
            UniqueConstraint(fields=["username"], name="uq__users__username"),
            UniqueConstraint(fields=["email"], name="uq__users__email"),
        ]

    def __str__(self) -> str:
        return self.username
