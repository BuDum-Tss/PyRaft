APPEND_RECORDS_ROUTE = "/append-records"
REQUEST_VOTE_ROUTE = "/request-vote"
UPDATE_ROUTE = "/update"


class ResponseError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self) -> str:
        return f"{self.status_code}: {self.message}"

