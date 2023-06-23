from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas import SettingUpdate
from crud import settings
from dependencies import get_db, validate_jwt

router = APIRouter()


@router.get("/settings/", dependencies=[Depends(validate_jwt)])
def read_settings(db: Session = Depends(get_db)):
    return {
        setting.value: settings.get_setting(db=db, setting=setting) for setting in settings.Settings
    }


@router.put("/settings/", dependencies=[Depends(validate_jwt)])
def update_settings(settings_schema: SettingUpdate, db: Session = Depends(get_db)):
    for key, value in settings_schema.settings.items():
        settings.set_setting(db=db, setting=settings.Settings(key), value=value)
