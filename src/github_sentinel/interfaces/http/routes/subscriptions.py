from uuid import UUID

from fastapi import APIRouter, Response, status

from github_sentinel.interfaces.http.dependencies import ApiKeyDependency, ContainerDependency
from github_sentinel.interfaces.http.schemas import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
    SyncResponse,
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: SubscriptionCreate,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> SubscriptionResponse:
    owner, name = payload.repository_parts
    subscription = container.subscriptions.create(
        owner=owner,
        name=name,
        schedule_type=payload.schedule_type,
        timezone=payload.timezone,
        event_types=frozenset(payload.event_types),
        notification_channels=tuple(payload.notification_channels),
    )
    return SubscriptionResponse.from_domain(subscription)


@router.get("", response_model=list[SubscriptionResponse])
def list_subscriptions(
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> list[SubscriptionResponse]:
    return [SubscriptionResponse.from_domain(item) for item in container.subscriptions.list()]


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: UUID,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> SubscriptionResponse:
    return SubscriptionResponse.from_domain(container.subscriptions.get(subscription_id))


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: UUID,
    payload: SubscriptionUpdate,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> SubscriptionResponse:
    updated = container.subscriptions.update(
        subscription_id,
        schedule_type=payload.schedule_type,
        timezone=payload.timezone,
        event_types=frozenset(payload.event_types) if payload.event_types else None,
        notification_channels=(
            tuple(payload.notification_channels)
            if payload.notification_channels is not None
            else None
        ),
        enabled=payload.enabled,
    )
    return SubscriptionResponse.from_domain(updated)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: UUID,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> Response:
    container.subscriptions.delete(subscription_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{subscription_id}/sync", response_model=SyncResponse)
def sync_subscription(
    subscription_id: UUID,
    container: ContainerDependency,
    _auth: ApiKeyDependency,
) -> SyncResponse:
    return SyncResponse.from_result(container.sync.sync(subscription_id))
