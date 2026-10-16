from collections.abc import Sequence
from datetime import UTC, datetime
from typing import NoReturn

from django.db import DatabaseError, IntegrityError

from library.adapters.database.tables import UserTable
from library.application.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    LibraryException,
)
from library.domains.entities.user import (
    CreateUser,
    UpdateUser,
    User,
    UserId,
    UserPaginationParams,
)
from library.domains.interfaces.storages.user import IUserStorage


class UserStorage(IUserStorage):
    def fetch_user_by_id(self, *, user_id: UserId) -> User | None:
        user = UserTable.objects.filter(id=user_id, deleted_at__isnull=True).first()

        if user is None:
            return None

        return User(
            id=UserId(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def exists_user_by_id(self, *, user_id: UserId) -> bool:
        return UserTable.objects.filter(id=user_id, deleted_at__isnull=True).exists()

    def count_users(self, *, params: UserPaginationParams) -> int:
        return UserTable.objects.filter(deleted_at__isnull=True)[
            params.offset : params.offset + params.limit
        ].count()

    def fetch_user_list(self, *, params: UserPaginationParams) -> Sequence[User]:
        result = UserTable.objects.filter(deleted_at__isnull=True).order_by("id")[
            params.offset : params.offset + params.limit
        ]
        return [
            User(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in result
        ]

    def create_user(self, *, user: CreateUser) -> User:
        try:
            result = UserTable.objects.create(
                username=user.username,
                email=user.email,
            )
        except IntegrityError as e:
            self._raise_error(e)
        return User(
            id=UserId(result.id),
            username=result.username,
            email=result.email,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    def delete_user_by_id(self, *, user_id: UserId) -> None:
        UserTable.objects.filter(id=user_id).update(deleted_at=datetime.now(tz=UTC))

    def update_user_by_id(self, *, update_user: UpdateUser) -> User:
        try:
            UserTable.objects.filter(id=update_user.id).update(**update_user.to_dict())
            result = UserTable.objects.get(id=update_user.id)
        except UserTable.DoesNotExist as e:
            raise EntityNotFoundException(entity=User, entity_id=update_user.id) from e
        except IntegrityError as e:
            self._raise_error(e)
        return User(
            id=UserId(result.id),
            username=result.username,
            email=result.email,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    def _raise_error(self, e: DatabaseError) -> NoReturn:
        constraint = e.__cause__.diag.constraint_name
        if constraint == "uq__users__username":
            raise EntityAlreadyExistsException("User already exists") from e
        elif constraint == "uq__users__email":
            raise EntityAlreadyExistsException("User already exists") from e
        raise LibraryException(message="Unknown error") from e
