class BookingApplication:
    def __init__(self, booking_system):
        self.booking_system = booking_system

    def book_seat(self, trip_number, passenger_name, seat_number):
        return self.booking_system.book_seat(
            trip_number,
            passenger_name,
            seat_number
        )

    def get_trip(self, trip_number):
        return self.booking_system.get_trip(trip_number)

    def get_available_trips(self):
        return self.booking_system.get_available_trips()
from src.Domain.ValueObject.setnumber import SeatNumber
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
        self._advertisement_service.refresh(trip, event)

        return BookSeatOutputDTO(
            booking_id=booking.booking_id,
            trip_number=booking.trip_number,
            passenger_name=booking.passenger_name,
            seat_number=int(booking.seat_number),
            available_seats=trip.available_seats,
        )