from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class SeatNumber:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise ValueError("Seat number must be an integer")
        if self.value <= 0:
            raise ValueError("Seat number must be positive")

    def __int__(self) -> int:
        return self.value