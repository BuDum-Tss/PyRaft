from fastapi import FastAPI, APIRouter, Depends
from fastapi.openapi.models import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import RedirectResponse

from pyraft.data.messages import AppendRecordsReq, RequestVoteReq, RequestVoteResp
from pyraft.core.transport import TransportService


def prepare_node_api(ts: TransportService) -> FastAPI:
    app = FastAPI(title="RAFT API", version="0.0.1")
    node_router = APIRouter()
    security = HTTPBearer()

    @app.get("/health")
    def health() -> str:
        return "Node is running!"

    app.redirect_url = property(lambda self: f"https://{ts.state.leader_id}/node/update")

    def check_authorization(credentials) -> bool:
        # TODO: normal check
        print(f" get: {credentials} - actual: {ts.settings.access_token}")
        return credentials == ts.settings.access_token

    @node_router.post("/append-records")
    def append_records(data: AppendRecordsReq, authorization: HTTPAuthorizationCredentials = Depends(security)):
        if check_authorization(authorization.credentials):
            return Response(status_code=401)
        return ts.append_records(data)

    @node_router.get("/request-vote")
    def request_vote(data: RequestVoteReq, authorization: HTTPAuthorizationCredentials = Depends(security)):
        if check_authorization(authorization.credentials):
            return Response(status_code=401)
        return ts.request_vote(data)

    @node_router.post("/update")
    def update(data: RequestVoteResp):
        if not ts.this_node_is_leader:
            return RedirectResponse(url=app.redirect_url)
        return ts.update(data)

    app.include_router(node_router, prefix="/node", tags=["node"])

    return app
