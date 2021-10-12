from datetime import date
from typing import Optional


class InvalidDueDate(Exception):
    ...


class Todo:
    def __init__(self, item_id: str, description: str, is_complete: bool, due: date):
        self.id = item_id
        self.description = description
        self.is_complete = is_complete
        self.due = due

    @property
    def due(self) -> date:
        return self._due

    @due.setter
    def due(self, due: date) -> None:
        today = date.today()
        if due < today:
            raise InvalidDueDate(f"Due date cannot be in the past.")
        else:
            self._due = due

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Todo):
            return False
        return other.id == self.id

    def __gt__(self, other) -> bool:
        return self.due > other.due

    def __repr__(self) -> str:
        return f"<Todo {self.id}>"
