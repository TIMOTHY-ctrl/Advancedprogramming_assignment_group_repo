from src.Domain.ValueObject.seatnumber import SeatNumber
from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO
from src.application.DTOs.BookSeatOutputDTO import BookSeatOutputDTO
from src.application.Repositories.ITripRepository import ITripRepository
from src.application.UseCases.UpdateAdvertisementService import (
    UpdateAdvertisementService,
)


class BookSeatService:
    def __init__(
        self,
        trip_repository: ITripRepository,
        advertisement_service: UpdateAdvertisementService,
    ) -> None:
        self._trip_repository = trip_repository
        self._advertisement_service = advertisement_service

    def execute(self, request: BookSeatInputDTO) -> BookSeatOutputDTO:
        trip = self._trip_repository.find_by_number(request.trip_number)
        if trip is None:
            raise ValueError(f"Trip {request.trip_number} does not exist")

        seat_number = SeatNumber(request.seat_number)
        booking, event = trip.book_seat(request.passenger_name, seat_number)
        self._trip_repository.save(trip)
        outcome = self._advertisement_service.refresh(trip, event)

        return BookSeatOutputDTO(
            booking_id=booking.booking_id,
            trip_number=booking.trip_number,
            passenger_name=booking.passenger_name,
            seat_number=int(booking.seat_number),
            available_seats=trip.available_seats,
            advertisement_outcome=outcome,
        )