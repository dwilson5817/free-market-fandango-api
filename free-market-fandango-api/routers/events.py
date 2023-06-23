from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..schemas import Event, EventCreate
from ..crud import events
from ..dependencies import get_db, validate_jwt

router = APIRouter()


@router.put("/events/", response_model=Event, dependencies=[Depends(validate_jwt)])
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    return events.create_event(db=db, event=event)


@router.get("/events/", response_model=list[Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_events = events.get_events(db, skip=skip, limit=limit)

    return db_events


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(validate_jwt)])
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = events.get_event(db=db, event_id=event_id)

    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    events.delete_event(db=db, event=db_event)


@router.get("/current_event/", response_model=Event)
def read_current_event(db: Session = Depends(get_db)):
    current_event = events.get_current_event(db=db)

    if not current_event:
        raise HTTPException(status_code=404, detail="No event is currently active")

    return current_event
