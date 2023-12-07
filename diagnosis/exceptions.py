class AIServerError(Exception):
    def __init__(self, message: str, extra_info: dict = None):
        super().__init__()
        self.extra_info = extra_info

    def __str__(self):
        return f'{super().__str__()} (AI Server information: {self.extra_info})'
