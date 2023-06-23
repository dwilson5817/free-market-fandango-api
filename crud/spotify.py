from sqlalchemy.orm import Session

import models


def get_token(db: Session) -> models.SpotifyToken:
    return db.query(models.SpotifyToken).first()


def create_token(db: Session, token_info: dict) -> models.SpotifyToken:
    db_token = get_token(db=db)

    if db_token:
        delete_token(db=db)

    db_token = models.SpotifyToken(**token_info)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


def delete_token(db: Session):
    db_token = get_token(db=db)

    db.delete(db_token)
    db.commit()
