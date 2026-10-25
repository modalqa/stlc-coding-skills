"""In-memory todo store."""
from dataclasses import dataclass
from itertools import count


class ValidationError(ValueError):
    pass


class NotFoundError(KeyError):
    pass


@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False


def _clean_title(title: str) -> str:
    title = (title or "").strip()
    if not 1 <= len(title) <= 100:
        raise ValidationError("title must be 1-100 characters")
    return title


class TodoStore:
    def __init__(self) -> None:
        self._items: dict[int, Todo] = {}
        self._ids = count(1)

    def create(self, title: str) -> Todo:
        todo = Todo(id=next(self._ids), title=_clean_title(title))
        self._items[todo.id] = todo
        return todo

    def list(self) -> list[Todo]:
        return list(self._items.values())

    def get(self, todo_id: int) -> Todo:
        try:
            return self._items[todo_id]
        except KeyError:
            raise NotFoundError(todo_id) from None

    def update(self, todo_id: int, title: str | None = None, completed: bool | None = None) -> Todo:
        todo = self.get(todo_id)
        if title is not None:
            todo.title = title.strip()
        if completed is not None:
            todo.completed = completed
        return todo

    def delete(self, todo_id: int) -> None:
        self._items.pop(todo_id, None)
