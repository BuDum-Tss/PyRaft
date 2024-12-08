import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import starlette.status as status

from pyraft import Node
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, SyncObjectModel, AppendRecordsResp, RequestVoteResp


def lifespan(api: FastAPI):
    print("startup")
    api.node.start()
    yield
    print("shutdown")

api = FastAPI(title="Raft API", version="1.0.0", lifespan=lifespan)
api.node: Node = None

@api.get("/", response_model=str)
def health() -> str:
    #logging.debug(f"RECEIVER - GET /health - STATUS: 200")
    return RedirectResponse("/docs")

@api.get("/health", response_model=str)
def health() -> str:
    #logging.debug(f"RECEIVER - GET /health - STATUS: 200")
    return "Node is running!"

@api.post("/append-records", response_model=AppendRecordsResp)
def append_records(request_data: AppendRecordsReq):
    #logging.debug(f"RECEIVER - POST /append-records - DATA: {request_data}")
    with api.node.receiver().state:
        return api.node.receiver().append_records(request_data)

@api.post("/request-vote", response_model=RequestVoteResp)
def request_vote(request_data: RequestVoteReq):
    #logging.debug(f"RECEIVER - POST /request-vote - DATA: {request_data}")
    with api.node.receiver().state:
        return api.node.receiver().request_vote(request_data)

@api.post("/set", response_model=str)
def set_value(request_data: SyncObjectModel):
    logging.info(f"RECEIVER - POST /set - DATA: {request_data}")
    with api.node.receiver().state:
        code, message = api.node.receiver().set_value(request_data)

    match code:
        case 301:
            redirect_url = f"https://{message}/node/update"
            logging.info(f"RECEIVER - POST /set - REDIRECT TO: {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)
        case _:
            logging.info(f"RECEIVER - POST /set - STATUS: {code}")
            return message

@api.get("/get/{key}")
def get_value(key: str):
    #logging.debug(f"RECEIVER - GET /set - DATA: {key}")
    return api.node.receiver().get_value(key)