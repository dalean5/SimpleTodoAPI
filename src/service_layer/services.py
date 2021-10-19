import logging
import os
import uuid
from datetime import date
from typing import List

from opencensus.ext.azure.log_exporter import AzureLogHandler
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from src.domain import model
from src.adapters.repository import AbstractTodoRepository

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(connection_string=os.environ["APP_INSIGHTS_INSTRUMENTATION_KEY"])
)


class NotFoundException(Exception):
    ...


def create_todo(
    description: str, is_complete: bool, due: date, repo: AbstractTodoRepository
) -> model.Todo:
    try:
        result = repo.create(
            model.Todo(
                item_id=str(uuid.uuid4()),
                description=description,
                is_complete=is_complete,
                due=due,
            )
        )
        return result
    except model.InvalidDueDate as e:
        logger.exception(str(e))
        raise model.InvalidDueDate(str(e))


def get_todo(item_id: str, repo: AbstractTodoRepository) -> model.Todo:
    try:
        return repo.get(item_id)
    except CosmosResourceNotFoundError as e:
        logger.exception(str(e))
        raise NotFoundException(f"Todo with id {item_id} not found.")


def list_todos(filters: dict, repo: AbstractTodoRepository) -> List[model.Todo]:
    if filters is None:
        filters = {}
    return repo.list(filters)


def update_todo(
    item_id: str,
    description: str,
    is_complete: bool,
    due: date,
    repo: AbstractTodoRepository,
) -> model.Todo:
    try:
        return repo.update(
            item_id,
            model.Todo(
                item_id=item_id,
                description=description,
                is_complete=is_complete,
                due=due,
            ),
        )
    except CosmosResourceNotFoundError as e:
        logger.exception(str(e))
        raise NotFoundException(f"Todo with id {item_id} not found.")
    except model.InvalidDueDate as e:
        logger.exception(str(e))
        raise model.InvalidDueDate(str(e))


def delete_todo(item_id: str, repo: AbstractTodoRepository) -> None:
    try:
        repo.delete(item_id)
    except CosmosResourceNotFoundError as e:
        logging.exception(str(e))
        raise NotFoundException(f"Todo with id {item_id} not found.")
