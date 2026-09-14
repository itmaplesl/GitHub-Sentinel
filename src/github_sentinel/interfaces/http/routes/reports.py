from uuid import UUID

from fastapi import APIRouter

from github_sentinel.domain.exceptions import EntityNotFoundError
from github_sentinel.interfaces.http.dependencies import ApiKeyDependency, ContainerDependency
from github_sentinel.interfaces.http.schemas import ReportCreate, ReportResponse

router = APIRouter(tags=["reports"])


@router.post(
    "/api/v1/subscriptions/{subscription_id}/reports",
    response_model=ReportResponse,
)
def create_report(
    subscription_id: UUID,
    payload: ReportCreate,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> ReportResponse:
    subscription = container.subscriptions.get(subscription_id)
    events = container.event_repository.list_for_period(
        subscription_id,
        payload.period_start,
        payload.period_end,
    )
    report = container.reports.generate(
        subscription,
        events,
        payload.period_start,
        payload.period_end,
    )
    return ReportResponse.from_domain(report)


@router.get("/api/v1/reports", response_model=list[ReportResponse])
def list_reports(
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> list[ReportResponse]:
    return [ReportResponse.from_domain(item) for item in container.report_repository.list()]


@router.get("/api/v1/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: UUID,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> ReportResponse:
    report = container.report_repository.get(report_id)
    if report is None:
        raise EntityNotFoundError(f"报告不存在: {report_id}")
    return ReportResponse.from_domain(report)
