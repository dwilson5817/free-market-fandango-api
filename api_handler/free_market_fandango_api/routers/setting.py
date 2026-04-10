from fastapi import APIRouter, Depends

from ..crud import setting
from ..dependencies import get_table, validate_jwt
from ..schemas import Setting, APIError
from ..utils import notify_cache_invalid_event


router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    dependencies=[Depends(get_table)],
)


@router.get(
    "",
    response_model=list[Setting],
    dependencies=[Depends(validate_jwt)],
    responses={
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
    },
)
def read_settings(table=Depends(get_table)):
    return setting.read_settings(table)


@router.put(
    "",
    response_model=list[Setting],
    dependencies=[Depends(validate_jwt)],
    responses={
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
    },
)
def update_settings(new_settings_list: list[Setting], table=Depends(get_table)):
    result = setting.update_settings(table, new_settings_list)

    notify_cache_invalid_event(table)

    return result
