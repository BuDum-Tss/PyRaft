from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from pyraft import Node
from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, SyncObjectModel, AppendRecordsResp, RequestVoteResp


def lifespan(api: FastAPI):
    api.node.start()
    yield
    api.node.stop()


api = FastAPI(title="Raft API", version="1.0.0", lifespan=lifespan)
api.node: Node = None


@api.get("/", response_model=str)
def health() -> str:
    return RedirectResponse("/docs")


@api.get("/health", response_model=str)
def health() -> str:
    return "Node is running!"


@api.post("/append-records", response_model=AppendRecordsResp)
def append_records(request_data: AppendRecordsReq):
    with api.node.receiver().state:
        return api.node.receiver().append_records(request_data)


@api.post("/request-vote", response_model=RequestVoteResp)
def request_vote(request_data: RequestVoteReq):
    with api.node.receiver().state:
        return api.node.receiver().request_vote(request_data)


@api.post("/set", response_model=str)
def set_value(request_data: SyncObjectModel):
    with api.node.receiver().state:
        code, message = api.node.receiver().set_value(request_data)
    return message


@api.get("/get/{key}")
def get_value(key: str):
    return api.node.receiver().get_value(key)
