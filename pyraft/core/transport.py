from fastapi.openapi.models import Response
from starlette.responses import RedirectResponse

from pyraft.data.settings import Settings
from pyraft.data.state import State
from pyraft.data.messages import RequestVoteReq, RequestVoteResp, AppendRecordsReq


class TransportService:
    def __init__(self, state: State, settings: Settings):
        self.settings = settings
        self.state = state

    def append_records(self, data: AppendRecordsReq):
        # TODO: implementation
        return Response(body={"term": 0, "success": True}, code=200)

    def request_vote(self, data: RequestVoteReq):
        # TODO: implementation
        return Response(body={"term": 0, "vote_granted": True}, code=200)

    def update(self, data: RequestVoteResp):
        # TODO: implementation
        return Response(code=200)

    @property
    def this_node_is_leader(self):
        return self.state.leader_id == self.settings.node_id
