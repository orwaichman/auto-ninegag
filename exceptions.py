class NoSuchElement(RuntimeError):
    pass


class AuthenticationRequired(RuntimeError):
    pass


class InvalidAction(RuntimeError):
    pass


class MissingWebdriver(FileNotFoundError):
    pass
