import logging
import requests
from pydantic import TypeAdapter

from pyraft.core.api import SenderApi
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, RequestVoteResp, AppendRecordsResp, SyncObjectModel

class HttpSender(SenderApi):

    def append_records(self, address: str, data: AppendRecordsReq, timeout: float = 10.0) -> AppendRecordsResp | None:
        logging.debug("append_records sended")
        with requests.Session() as session:
            route = "/append-records"
            url = f"http://{address}{route}"
            logging.debug(f"SENDER - \"POST /append-records - DATA: {data.model_dump_json()}")
            try:
                response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                           headers={"Content-Type": "application/json"},
                                                           timeout=timeout)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                logging.error(f"SENDER - POST /append-records - ConnectionError")
                return None
            if response.status_code == 200:
                logging.debug(f"SENDER - POST /append-records - RESPONSE: {response.text}")
                return TypeAdapter(type=AppendRecordsResp).validate_json(response.text)
            return None

    def request_vote(self, address: str, data: RequestVoteReq, timeout: float = 10.0) -> RequestVoteResp | None:
        with requests.Session() as session:
            route ="/request-vote"
            url = f"http://{address}{route}"
            logging.debug(f"SENDER - POST /request-vote")
            try:
                response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                           headers={"Content-Type": "application/json"},
                                                           timeout=timeout)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                logging.error(f"SENDER - POST /request-vote - ConnectionError")
                return None
            if response.status_code == 200:
                logging.debug(f"SENDER - POST /request-vote - RESPONSE: {response.text}")
                return TypeAdapter(type=RequestVoteResp).validate_json(response.text)
            return None


#    def set_value(self, address: str, data: SetValueReq, timeout: float = 10.0) -> int | None:
#        with requests.Session() as session:
#            url = self.url(address, "/set")
#            try:
#                response: requests.Response = session.post(url, data=data.model_dump_json(),
#                                                           headers={"Content-Type": "application/json"},
#                                                           timeout=timeout)
#            except requests.exceptions.ConnectionError:
#                logging.error(f"SENDER - POST /set - ConnectionError")
#            if response.status_code == 200:
#                logging.debug(f"SENDER - POST /set - RESPONSE: {response.text}")
#            return response.status_code
