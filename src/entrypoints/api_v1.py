from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse

import config
from src.adapters import repository
from src.service_layer import services
from src.domain.model import InvalidDueDate

router = APIRouter(prefix="/todos", tags=["todos"])

repo = repository.AzureCosmosRepository(config.get_cosmos_container_client())


@router.post("/")
def create_todo(
    description: str = Body(...), is_complete: bool = Body(...), due: date = Body(...)
):
    try:
        result = services.create_todo(description, is_complete, due, repo)
        return JSONResponse(
            status_code=200, content=repository.convert_domain_model_to_dict(result)
        )
    except InvalidDueDate as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_id}")
def get_todo(item_id: str):
    try:
        result = services.get_todo(item_id, repo)
        return JSONResponse(
            status_code=200, content=repository.convert_domain_model_to_dict(result)
        )
    except services.NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_todos():
    results = services.list_todos({}, repo)
    return JSONResponse(
        status_code=200,
        content=[repository.convert_domain_model_to_dict(r) for r in results],
    )


@router.put("/{item_id}")
def update_todo(
    item_id: str,
    description: str = Body(...),
    is_complete: bool = Body(...),
    due: date = Body(...),
):
    try:
        result = services.update_todo(item_id, description, is_complete, due, repo)
        return JSONResponse(
            status_code=200, content=repository.convert_domain_model_to_dict(result)
        )
    except InvalidDueDate as e:
        raise HTTPException(status_code=400, detail=str(e))
    except services.NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{item_id}")
def delete_todo(item_id: str):
    try:
        services.delete_todo(item_id, repo)
        return JSONResponse(status_code=204, content=None)
    except services.NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
