import uuid
from datetime import date, timedelta

import pytest
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from src.adapters import repository
from src.domain import model

today = date.today()
tomorrow = today + timedelta(days=1)


@pytest.mark.slow
def test_repository_can_save_todo(cosmos_container_client):
    repo = repository.AzureCosmosRepository(cosmos_container_client)
    todo = model.Todo(
        item_id=str(uuid.uuid4()),
        description="A Sample Todo",
        is_complete=False,
        due=today,
    )

    result = repo.create(todo)
    assert result is not None
    assert isinstance(result, model.Todo)
    assert result.description == todo.description
    assert result.is_complete == todo.is_complete
    assert result.due == todo.due


@pytest.mark.slow
def test_repository_can_get_item_by_id(cosmos_container_client):
    repo = repository.AzureCosmosRepository(cosmos_container_client)
    todo = model.Todo(
        item_id=str(uuid.uuid4()),
        description="A Sample Todo",
        is_complete=False,
        due=today,
    )

    repo.create(todo)
    retrieved_todo = repo.get(todo.id)

    assert retrieved_todo is not None
    assert isinstance(retrieved_todo, model.Todo)


@pytest.mark.slow
def test_repository_can_list_todos(cosmos_container_client):
    repo = repository.AzureCosmosRepository(cosmos_container_client)
    todo = model.Todo(
        item_id=str(uuid.uuid4()),
        description="A Sample Todo",
        is_complete=False,
        due=today,
    )
    repo.create(todo)

    result = repo.list()
    assert isinstance(result, list)
    assert isinstance(result[0], model.Todo)


@pytest.mark.slow
def test_repository_can_update_todo(cosmos_container_client):
    # create todo item in cosmos container
    item_id = str(uuid.uuid4())
    cosmos_container_client.create_item(
        {"id": item_id, "description": "Test Todo", "is_complete": False, "due": today.isoformat()}
    )

    # update todo
    repo = repository.AzureCosmosRepository(cosmos_container_client)
    repo.update(item_id=item_id, todo=model.Todo(item_id, "I was updated!", True, tomorrow))

    # get the updated todo and assert its values
    retrieved_todo = repo.get(item_id)
    assert retrieved_todo.id == item_id
    assert retrieved_todo.description == "I was updated!"
    assert retrieved_todo.is_complete is True
    assert retrieved_todo.due == tomorrow


@pytest.mark.slow
def test_repository_can_delete_todo(cosmos_container_client):
    # create todo item in cosmos container
    item_id = str(uuid.uuid4())
    cosmos_container_client.create_item(
        {"id": item_id, "description": "Test Todo", "is_complete": False, "due": today.isoformat()}
    )

    # delete todo
    repo = repository.AzureCosmosRepository(cosmos_container_client)
    repo.delete(item_id)

    with pytest.raises(CosmosResourceNotFoundError):
        repo.get(item_id)
