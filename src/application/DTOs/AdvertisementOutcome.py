from dataclasses import dataclass
from enum import Enum


class AdvertisementStatus(Enum):
    ADVERTISED = 'advertised'
    WITHDRAWN = 'withdrawn'
    REJECTED = 'rejected'


class RejectionReason(Enum):
    MISSING = 'advertisement does not exist'
    ALREADY_WITHDRAWN = 'advertisement already withdrawn'


@dataclass(frozen=True)
class AdvertisementOutcome:
    status: AdvertisementStatus
    reason: RejectionReason | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, AdvertisementStatus):
            raise ValueError('Unknown advertisement status')
        if (self.status is AdvertisementStatus.REJECTED) != (self.reason is not None):
            raise ValueError('Only rejected outcomes require a reason')
        if self.reason is not None and not isinstance(self.reason, RejectionReason):
            raise ValueError('Unknown rejection reason')

    def __str__(self) -> str:
        return self.status.value if self.reason is None else f'{self.status.value}: {self.reason.value}'
