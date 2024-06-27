from fastapi import HTTPException, status


class MessengerException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(MessengerException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class UsersNotExistsException(MessengerException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь по данному id не существует"


class IncorrectEmailOrPasswordException(MessengerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(MessengerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(MessengerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(MessengerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class UserIsNotPresentException(MessengerException):
    status_code = status.HTTP_401_UNAUTHORIZED


class NullDataException(MessengerException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Данные для загрузки не могут быть пустыми"


class CannotReplacePasswordException(MessengerException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Не удалось изменить пароль"
