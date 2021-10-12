from datetime import date, timedelta
import pytest

from src.domain import model

today = date.today()
later = today + timedelta(days=5)
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)


def test_todo_raise_exception_on_invalid_datetime():
    with pytest.raises(model.InvalidDueDate, match="Due date cannot be in the past."):
        model.Todo("todo-1", "A Sample Todo", False, yesterday)


def test_todo_can_be_sorted():
    today_todo = model.Todo("todo-1", "I am Todo #1", False, today)
    tomorrow_todo = model.Todo("todo-2", "I am Todo #2", False, tomorrow)
    later_todo = model.Todo("todo-3", "I am Todo #3", False, later)

    sorted_todos = sorted([tomorrow_todo, today_todo, later_todo])

    assert sorted_todos[0].id == "todo-1"
    assert sorted_todos[1].id == "todo-2"
    assert sorted_todos[2].id == "todo-3"
