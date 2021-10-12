import logging
import os
from urllib.parse import quote_plus

from azure.cosmos.container import ContainerProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos import CosmosClient

logger = logging.getLogger(__name__)


def get_cosmos_container_client() -> ContainerProxy:
    try:
        connection_string = os.environ["COSMOS_CONNECTION_STRING"]
        database_name = os.environ["COSMOS_DATABASE"]
        container_name = os.environ["COSMOS_CONTAINER"]
        cosmos_client = CosmosClient.from_connection_string(connection_string)
        database_client = cosmos_client.get_database_client(database_name)
        container_client = database_client.get_container_client(container_name)
        return container_client
    except (CosmosResourceNotFoundError, KeyError) as e:
        logger.exception(str(e))
        exit(-1)


def get_postgres_uri() -> str:
    try:
        host = os.environ["DB_HOST"]
        user = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        name = os.environ["DB_NAME"]
        port = os.environ["DB_PORT"]

        return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{name}"

    except KeyError as e:
        logger.exception(str(e))
        exit(-1)
