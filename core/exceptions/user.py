from core.exceptions.base import CoreError


class UserAlreadyExistsError(CoreError):
    def __init__(self, phone: str, message=None):
        self.phone = phone
        super().__init__(message)


class BirthdayCanBeChangedOnceError(CoreError):
    pass


class BadAvatarError(CoreError):
    pass


class BadAvatarResolutionError(BadAvatarError):
    pass


class BadAvatarSizeError(BadAvatarError):
    pass


class BadAvatarTypeError(BadAvatarError):
    pass
