KEY = "SpotifyToken"


def _item_to_dict(item):
    return {
        "access_token": item["AccessToken"],
        "token_type": item["TokenType"],
        "expires_in": item["ExpiresIn"],
        "scope": item["Scope"],
        "expires_at": item["ExpiresAt"],
        "refresh_token": item["RefreshToken"],
    }


def read_spotify_token(table):
    response = table.get_item(
        Key={
            "PK": KEY,
            "SK": KEY,
        }
    )

    if "Item" not in response:
        return None

    return _item_to_dict(response["Item"])


def update_spotify_token(table, token):
    print(token)

    table.put_item(
        Item={
            "PK": KEY,
            "SK": KEY,
            "AccessToken": token["access_token"],
            "TokenType": token["token_type"],
            "ExpiresIn": token["expires_in"],
            "Scope": token["scope"],
            "ExpiresAt": token["expires_at"],
            "RefreshToken": token["refresh_token"],
        }
    )


def delete_spotify_token(table):
    table.delete_item(
        Key={
            "PK": KEY,
            "SK": KEY,
        }
    )
