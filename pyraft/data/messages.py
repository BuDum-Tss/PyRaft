from typing import List
from pydantic import BaseModel


class SyncObjectModel(BaseModel):
    key: str
    value: str


class Record(SyncObjectModel):
    term: int
    key: str
    value: str


class AppendRecordsReq(BaseModel):
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    records: List[Record]
    commit: int


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
