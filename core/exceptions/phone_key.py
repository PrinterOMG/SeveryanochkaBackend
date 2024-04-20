from core.exceptions.base import CoreError


class PhoneKeyCreateLimitError(CoreError):
    pass


class BadPhoneKeyError(CoreError):
    pass


class BadConfirmationCodeError(CoreError):
    def __init__(self, confirmation_code, message=None):
        self.confirmation_code = confirmation_code
        super().__init__(message)
