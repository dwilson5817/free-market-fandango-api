from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from ..crud import event
from ..dependencies import get_table, validate_jwt
from ..schemas import EventIn, EventOut

router = APIRouter(
    prefix="/event",
    tags=["events"],
    dependencies=[Depends(get_table)],
)


@router.put(
    "",
    response_model=EventOut,
    dependencies=[Depends(validate_jwt)]
)
def create_event(new_event: EventIn, table=Depends(get_table)):
    return event.update_event(table, new_event)


@router.get(
    "",
    response_model=list[EventOut]
)
def read_events(table=Depends(get_table)):
    return event.read_events(table)


@router.get(
    "/{event_id}",
    response_model=list[EventOut],
    responses={
        404: {"description": "Not found"}
    }
)
def read_event(event_id: UUID, table=Depends(get_table)):
    response = event.read_event(table, event_id)

    if response is None:
        raise HTTPException(status_code=404, detail="Event does not exist")

    return response


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_jwt)],
)
def delete_event(event_id: str, table=Depends(get_table)):
    event.delete_event(table, event_id)

    return Response(status_code=HTTP_204_NO_CONTENT)
