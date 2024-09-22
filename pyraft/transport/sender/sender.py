import logging
from typing import Callable

import requests
from pydantic import TypeAdapter

from pyraft.core.api import SenderApi
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, RequestVoteResp, AppendRecordsResp, UpdateValueReq
from pyraft.transport.utils import ResponseError, APPEND_RECORDS_ROUTE, REQUEST_VOTE_ROUTE, UPDATE_ROUTE
from test.log import set_logging

set_logging(logging.DEBUG)


class HttpSender(SenderApi):

    def append_records(self, address: str, data: AppendRecordsReq) -> AppendRecordsResp:
        with requests.Session() as session:
            url = self.url(address, APPEND_RECORDS_ROUTE)
            logging.debug(f"SENDER - POST {APPEND_RECORDS_ROUTE} - DATA: {data.model_dump_json()}")
            response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                       headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                logging.debug(f"SENDER - POST {APPEND_RECORDS_ROUTE} - RESPONSE: {response.text}")
                return TypeAdapter(type=AppendRecordsResp).validate_json(response.text)
            else:
                raise ResponseError(response.status_code, response.text)

    def request_vote(self, address: str, data: RequestVoteReq) -> RequestVoteResp:
        with requests.Session() as session:
            url = self.url(address, REQUEST_VOTE_ROUTE)
            response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                       headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                logging.debug(f"SENDER - POST {REQUEST_VOTE_ROUTE} - RESPONSE: {response.text}")
                return TypeAdapter(type=RequestVoteResp).validate_json(response.text)
            else:
                raise ResponseError(response.status_code, response.text)

    def update(self, address: str, data: UpdateValueReq):
        with requests.Session() as session:
            url = self.url(address, UPDATE_ROUTE)
            response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                       headers={"Content-Type": "application/json"})
            if response.status_code != 200:
                raise ResponseError(response.status_code, response.text)
            else:
                logging.debug(f"SENDER - POST {UPDATE_ROUTE} - RESPONSE: {response.text}")

    def url(self, address: str, route: str) -> str:
        return f"http://{address}{route}"
