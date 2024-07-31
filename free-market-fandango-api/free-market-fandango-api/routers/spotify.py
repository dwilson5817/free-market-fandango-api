from fastapi import APIRouter, Depends, HTTPException
from spotipy import CacheHandler, Spotify, SpotifyOAuth
from starlette.responses import Response

from ..crud import spotify
from ..dependencies import get_table, validate_jwt
from ..schemas import SpotifyConnectRequest, SpotifyAccountResponse, APIError, SpotifyRedirectResponse, \
    SpotifyCurrentlyPlayingResponse

router = APIRouter(
    prefix="/spotify",
    tags=["spotify"],
    dependencies=[Depends(get_table)],
)


class SettingsCacheHandler(CacheHandler):
    def __init__(self, table):
        self.table = table

    def get_cached_token(self):
        return spotify.read_spotify_token(self.table)

    def save_token_to_cache(self, token_info):
        spotify.update_spotify_token(self.table, token_info)


class SpotifyHandler:
    def __init__(self, table):
        self._table = table
        self._spotify_cache = SettingsCacheHandler(self._table)
        self._spotify_oauth = SpotifyOAuth(
            scope="user-read-currently-playing", cache_handler=self._spotify_cache
        )
        self._spotify = Spotify(auth_manager=self._spotify_oauth)

    def get_auth_url(self):
        return self._spotify_oauth.get_authorize_url()

    def save_auth_token(self, code):
        self._spotify_oauth.get_access_token(code)

    def is_logged_in(self):
        return True if self._spotify_oauth.get_cached_token() else False

    def get_account_info(self):
        return self._spotify.current_user()

    def currently_playing(self):
        if self.is_logged_in() and self._spotify.currently_playing():
            return self._spotify.currently_playing()
        else:
            return False


@router.get(
    "/account",
    response_model=SpotifyAccountResponse,
    responses={
        400: {
            "description": "No account connected, connect an account first",
            "model": APIError,
        }
    },
)
async def spotify_account_info(table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)

    if not spotify_handler.is_logged_in():
        raise HTTPException(status_code=400, detail="No account connected, connect an account first")

    account_info = spotify_handler.get_account_info()

    if not account_info:
        raise HTTPException(status_code=400, detail="No account connected, connect an account first")

    return SpotifyAccountResponse(
        display_name=account_info["display_name"],
        profile_picture=account_info["images"][0]["url"]
    )


@router.get(
    "/redirect",
    response_model=SpotifyRedirectResponse,
    dependencies=[Depends(validate_jwt)],
)
async def spotify_redirect_for_authz(table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)

    return SpotifyRedirectResponse(
        redirect_url=spotify_handler.get_auth_url()
    )


@router.post(
    "/connect",
    dependencies=[Depends(validate_jwt)],
    status_code=204
)
async def save_auth_token(request: SpotifyConnectRequest, table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)
    spotify_handler.save_auth_token(request.auth_code)

    return Response(status_code=204)


@router.post(
    "/disconnect",
    dependencies=[Depends(validate_jwt)],
    status_code=204
)
async def delete_auth_token(table=Depends(get_table)):
    spotify.delete_spotify_token(table=table)

    return Response(status_code=204)


@router.get(
    "/currently_playing",
    response_model=SpotifyCurrentlyPlayingResponse,
    responses={
        400: {
            "description": "No account connected or nothing is playing",
            "model": APIError,
        }
    },
)
async def get_spotify_currently_playing(table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)

    if not spotify_handler.is_logged_in():
        raise HTTPException(status_code=400, detail="No account connected, connect an account first")

    currently_playing = spotify_handler.currently_playing()

    if not currently_playing:
        raise HTTPException(status_code=400, detail="Nothing is currently playing")

    return SpotifyCurrentlyPlayingResponse(
        title=currently_playing["item"]["name"],
        album=currently_playing["item"]["album"]["name"],
        artists=", ".join(
                [artist["name"] for artist in currently_playing["item"]["album"]["artists"]]
            ),
        artwork_url=currently_playing["item"]["album"]["images"][1]["url"],
        progress_ms=currently_playing["progress_ms"],
        duration_ms=currently_playing["item"]["duration_ms"]
    )
