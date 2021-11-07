from fastapi import Depends, FastAPI, HTTPException

from src.auth import AuthHandler
from src.database import get_session
from src.models.auth import UserDBModel
from src.schemas import AuthDetails

auth_handler = AuthHandler()
session = get_session
app = FastAPI(prefix="/auth", tags=["auth"])


@app.post("/register", status_code=201)
def register(auth_details: AuthDetails):
    """Регистрация пользователя в систсеме.

    Args:
        auth_details: Авторизационные данные.

    Raises:
        HTTPException: Ошибка при регистрации данных.
    """
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    user = UserDBModel(
        username=auth_details.username,
        password_hash=hashed_password,
    )
    session.add(user)
    session.commit()
    return


@app.post("/login")
def login(auth_details: AuthDetails):
    """Вход в систему.

    Args:
        auth_details Авторизационные данные.

    Raises:
        HTTPException: Ошибка при авторизации.

    Returns:
        Токен для авторизации в системе.
    """
    user = UserDBModel.query.filter_by(username=auth_details.username).one_or_none()

    if (user is None) or (
        not auth_handler.verify_password(auth_details.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    token = auth_handler.encode_token(user["username"])
    return {"token": token}


@app.get("/protected")
def protected(username=Depends(auth_handler.decode_token)):
    return {"name": username}
