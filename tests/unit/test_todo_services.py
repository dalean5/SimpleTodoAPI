from datetime import date, timedelta
from typing import List

import pytest
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from src.adapters import repository
from src.domain import model
from src.service_layer import services

today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)


class FakeRepository(repository.AbstractTodoRepository):
    def __init__(self, data: list = []):
        self._data = set(data)

    def create(self, todo: model.Todo) -> model.Todo:
        self._data.add(todo)
        return todo

    def get(self, item_id: str) -> model.Todo:
        try:
            return next(t for t in self._data if t.id == item_id)
        except StopIteration:
            raise CosmosResourceNotFoundError(status_code=404)

    def list(self, filters: dict = {}) -> List[model.Todo]:
        return list(self._data)

    def update(self, item_id: str, todo: model.Todo) -> model.Todo:
        try:
            t = next(t for t in self._data if t.id == item_id)
            self._data.remove(t)
            self._data.add(todo)
            return todo
        except StopIteration:
            raise CosmosResourceNotFoundError(status_code=404)

    def delete(self, item_id: str) -> None:
        try:
            t = next(t for t in self._data if t.id == item_id)
            self._data.remove(t)
        except StopIteration:
            raise CosmosResourceNotFoundError(status_code=404)


def test_services_can_create_todo():
    repo = FakeRepository([])
    todo_dict = {"description": "A Sample Todo", "is_complete": False, "due": today}
    result = services.create_todo(**todo_dict, repo=repo)
    assert repo._data is not None
    assert isinstance(result, model.Todo)


def test_services_can_get_todo():
    repo = FakeRepository([
        model.Todo("1", "A Sample Todo", False, today)
    ])

    result = services.get_todo("1", repo)
    assert result is not None
    assert isinstance(result, model.Todo)


def test_services_can_list_todos():
    repo = FakeRepository([
        model.Todo("1", "A Sample Todo", False, today),
        model.Todo("2", "Another Sample Todo", True, tomorrow)
    ])

    results = services.list_todos(filters={}, repo=repo)
    assert results is not None
    assert isinstance(results, list)


def test_services_can_update_todo():
    repo = FakeRepository([
        model.Todo("1", "A Sample Todo", False, today)
    ])

    update_dict = {"description": "Updated Todo", "is_complete": True, "due": tomorrow}
    services.update_todo("1", **update_dict, repo=repo)

    assert list(repo._data)[0].id == "1"
    assert list(repo._data)[0].description == "Updated Todo"


def test_services_can_delete_todo():
    repo = FakeRepository([
        model.Todo("1", "A Sample Todo", False, today)
    ])

    services.delete_todo("1", repo)

    assert len(list(repo._data)) == 0


def test_service_raises_exception_on_get_it_todo_not_found():
    repo = FakeRepository([])

    with pytest.raises(services.NotFoundException):
        services.get_todo("1", repo)


def test_service_raises_exception_on_create_if_invalid_todo_date():
    repo = FakeRepository([])

    with pytest.raises(model.InvalidDueDate):
        services.create_todo("Invalid Todo", False, yesterday, repo)


def test_service_raises_exception_on_update_if_todo_not_found():
    repo = FakeRepository([])

    with pytest.raises(services.NotFoundException):
        update_dict = {"description": "Updated Todo", "is_complete": True, "due": tomorrow}
        services.update_todo("1", **update_dict, repo=repo)


def test_service_raises_exception_on_delete_if_todo_not_found():
    repo = FakeRepository([])

    with pytest.raises(services.NotFoundException):
        services.delete_todo("1", repo)