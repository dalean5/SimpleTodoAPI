import abc
import uuid
from datetime import date
from typing import Optional, List

from azure.cosmos.container import ContainerProxy

from src.domain import model


def convert_dict_to_domain_model(data: dict) -> model.Todo:
    try:
        todo_model = model.Todo(
            item_id=data["id"],
            description=data["description"],
            is_complete=data["is_complete"],
            due=date.fromisoformat(data["due"])
        )
        return todo_model
    except KeyError:
        return None


def convert_domain_model_to_dict(todo: model.Todo) -> dict:
    return {
        "id": todo.id,
        "description": todo.description,
        "is_complete": todo.is_complete,
        "due": todo.due.isoformat(),
    }


class AbstractTodoRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, todo: model.Todo) -> model.Todo:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, item_id: str) -> model.Todo:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, filters: dict = {}) -> List[model.Todo]:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, item_id: str, todo: model.Todo) -> model.Todo:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError


class AzureCosmosRepository(AbstractTodoRepository):
    def __init__(self, container_client):
        self.container: ContainerProxy = container_client

    def create(self, todo: model.Todo) -> model.Todo:
        created_todo = self.container.create_item(body=convert_domain_model_to_dict(todo))
        return convert_dict_to_domain_model(created_todo)

    def get(self, item_id: str) -> model.Todo:
        retrieved_todo = self.container.read_item(item=item_id, partition_key=item_id)
        return convert_dict_to_domain_model(retrieved_todo)

    def list(self, filters: dict = {}) -> List[model.Todo]:
        retrieved_todos = list(self.container.read_all_items(max_item_count=10))  # Implement offset
        if len(retrieved_todos) == 0:
            return []

        todos_list = []
        for t in retrieved_todos:
            todos_list.append(convert_dict_to_domain_model(t))

        return todos_list

    def update(self, item_id: str, todo: model.Todo) -> model.Todo:
        retrieved_todo = self.container.read_item(item=item_id, partition_key=item_id)
        retrieved_todo["description"] = todo.description
        retrieved_todo["is_complete"] = todo.is_complete
        retrieved_todo["due"] = todo.due.isoformat()

        updated_todo = self.container.upsert_item(body=retrieved_todo)
        return convert_dict_to_domain_model(updated_todo)

    def delete(self, item_id: str) -> None:
        self.container.delete_item(item=item_id, partition_key=item_id)
