from fastapi import APIRouter, Depends
from spotipy import CacheHandler, Spotify, SpotifyOAuth
from starlette.responses import RedirectResponse, Response

from ..crud import spotify
from ..dependencies import get_table, validate_jwt

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


@router.get("/account_info/")
async def spotify_account_info(table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)

    if not spotify_handler.is_logged_in():
        return False

    account_info = spotify_handler.get_account_info()

    if not account_info:
        return False

    response = {
        "name": account_info["display_name"],
        "profile_picture": account_info["images"][0]["url"],
    }

    return response


@router.get("/redirect/", response_class=RedirectResponse)
async def spotify_redirect_for_authz(table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)

    return spotify_handler.get_auth_url()


@router.get("/connect")
async def save_auth_token(code: str, table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)
    spotify_handler.save_auth_token(code)

    data = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Spotify connected</title>
      </head>
      <body>
        <h2>Spotify connected</h2>
        <p>You may now close this tab.</p>
        <a href="#" onclick="close_window();return false;">Close tab</a>
      </body>
    </html>
    """

    return Response(content=data, media_type="text/html")


@router.get("/disconnect/", dependencies=[Depends(validate_jwt)])
async def delete_auth_token(table=Depends(get_table)):
    spotify.delete_spotify_token(table=table)

    return {"message": "Spotify account disconnected successfully."}


@router.get("/currently_playing/")
async def get_spotify_currently_playing(table=Depends(get_table)):
    spotify_handler = SpotifyHandler(table=table)

    if not spotify_handler.is_logged_in():
        return False

    currently_playing = spotify_handler.currently_playing()

    if not currently_playing:
        return False

    response = {
        "name": currently_playing["item"]["name"],
        "album": currently_playing["item"]["album"]["name"],
        "artists": ", ".join(
            [artist["name"] for artist in currently_playing["item"]["album"]["artists"]]
        ),
        "artwork": currently_playing["item"]["album"]["images"][1]["url"],
        "progress_ms": currently_playing["progress_ms"],
        "duration_ms": currently_playing["item"]["duration_ms"],
    }

    return response
