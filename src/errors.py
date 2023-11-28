class ForbiddenOperation(Exception):
    def __init__(self) -> None:
        super().__init__('Forbidden Operation')

class GuildOperation(Exception):
    def __init__(self) -> None:
        super().__init__('Cannot use this command out of a server.')

class ParameterError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f'ParameterError: {message}')
