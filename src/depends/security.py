from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


oauth2scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def get_current_user(token: str = Depends(oauth2scheme)):
    return token
