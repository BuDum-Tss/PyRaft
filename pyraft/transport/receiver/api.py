import logging
from typing import Callable

from flask import request, Response
from flask_classful import FlaskView, route
from pydantic import TypeAdapter

from pyraft.core.api import ReceiverApi
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, UpdateValueReq
from pyraft.transport.utils import APPEND_RECORDS_ROUTE, REQUEST_VOTE_ROUTE, UPDATE_ROUTE


class NodeApi(FlaskView):
    def __init__(self, receiver: Callable[[], ReceiverApi], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver = receiver

    @route("/health", methods=["GET"])
    def health(self) -> str:
        logging.debug(f"RECEIVER - GET /health - STATUS: 200")
        return "Node is running!"

    @route(APPEND_RECORDS_ROUTE, methods=['POST'])
    def append_records(self):
        logging.debug(f"RECEIVER - POST {APPEND_RECORDS_ROUTE} - DATA: {request.get_json()}")
        data = TypeAdapter(type=AppendRecordsReq).validate_python(request.get_json())
        return self.receiver().append_records(data).model_dump_json()

    @route(REQUEST_VOTE_ROUTE, methods=['POST'])
    def request_vote(self):
        logging.debug(f"RECEIVER - POST {REQUEST_VOTE_ROUTE} - DATA: {request.get_json()}")
        data = TypeAdapter(type=RequestVoteReq).validate_python(request.get_json())
        return self.receiver().request_vote(data).model_dump_json()

    @route(UPDATE_ROUTE, methods=['POST'])
    def update(self):
        logging.debug(f"RECEIVER - POST {UPDATE_ROUTE} - DATA: {request.get_json()}")
        data = TypeAdapter(type=UpdateValueReq).validate_python(request.get_json())
        code, message = self.receiver().update(data)
        match code:
            case 301:
                redirect_url = f"https://{message}/node/update"
                logging.debug(f"RECEIVER - POST {UPDATE_ROUTE} - REDIRECT TO: {redirect_url}")
                return Response(headers={"Location": redirect_url}, status=301)
            case _:
                logging.debug(f"RECEIVER - POST {UPDATE_ROUTE} - STATUS: {code}")
                return Response(response={"message": message}, status=code)
