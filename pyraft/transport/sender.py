import logging
import requests

from pydantic import TypeAdapter

from pyraft.core.api import SenderApi
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, RequestVoteResp, AppendRecordsResp, SyncObjectModel

log = logging.getLogger("SENDER")

class HttpSender(SenderApi):

    def append_records(self, address: str, data: AppendRecordsReq, timeout: float = 10.0) -> AppendRecordsResp | None:
        with requests.Session() as session:
            url = f"http://{address}/append-records"
            try:
                response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                           headers={"Content-Type": "application/json"},
                                                           timeout=timeout)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                log.error(f"{address} - \"POST /append-records\" ConnectionError\n"
                          f"DATA: {data.model_dump_json()}")
                return None
            log.info(f"{address} - \"POST /append-records\" {response.status_code}\n"
                     f"DATA: {data.model_dump_json()}\nRESPONSE: {response.text}")
            if response.status_code == 200:
                return TypeAdapter(type=AppendRecordsResp).validate_json(response.text)
            return None

    def request_vote(self, address: str, data: RequestVoteReq, timeout: float = 10.0) -> RequestVoteResp | None:
        with requests.Session() as session:
            url = f"http://{address}/request-vote"
            try:
                response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                           headers={"Content-Type": "application/json"},
                                                           timeout=timeout)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                log.error(f"{address} - \"POST /request-vote\" ConnectionError\n"
                          f"DATA: {data.model_dump_json()}")
                return None
            log.info(f"{address} - \"POST /request-vote\" {response.status_code}\n"
                     f"DATA: {data.model_dump_json()}\nRESPONSE: {response.text}")
            if response.status_code == 200:
                return TypeAdapter(type=RequestVoteResp).validate_json(response.text)
            return None

    def set_value(self, address: str, data: SyncObjectModel, timeout: float = 10.0) -> tuple[int, str]:
        with requests.Session() as session:
            url = f"http://{address}/set"
            try:
                response: requests.Response = session.post(url, data=data.model_dump_json(),
                                                           headers={"Content-Type": "application/json"},
                                                           timeout=timeout)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                log.error(f"{address} - \"POST /set\" ConnectionError\n"
                          f"DATA: {data.model_dump_json()}")
                return 301, "Leader unavailable"
            log.info(f"{address} - \"POST /set\" {response.status_code}\n"
                     f"DATA: {data.model_dump_json()}\nRESPONSE: {response.text}")
            return response.status_code, response.text.strip('"')