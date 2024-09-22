from typing import List

from pydantic import BaseModel


class Record(BaseModel):
    index: int
    shared_object_id: str
    value: str


class AppendRecordsReq(BaseModel):
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_index: int
    entries: List[Record]


class AppendRecordsResp(BaseModel):
    term: int
    success: bool


class RequestVoteReq(BaseModel):
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int


class RequestVoteResp(BaseModel):
    term: int
    vote_granted: bool


class UpdateValueReq(BaseModel):
    shared_object_id: str
    value: str
