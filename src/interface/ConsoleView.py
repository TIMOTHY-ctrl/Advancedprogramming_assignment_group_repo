from collections.abc import Callable, Iterable
from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Aggregate.TripAdvertisementAggregate.TripAdvertisement import TripAdvertisement
from src.application.DTOs.BookSeatOutputDTO import BookSeatOutputDTO


class ConsoleView:
    """Presentation and terminal I/O only; no booking decisions."""

    def __init__(self, input_fn: Callable[[str], str] = input,
                 output_fn: Callable[[str], None] = print) -> None:
        self._input = input_fn
        self._output = output_fn

    def read(self, prompt: str) -> str:
        return self._input(prompt).strip()

    def menu(self) -> None:
        self._output('')
        for line in ['1. Show trips with available seats', '2. Book a seat',
                     '3. Retrieve a trip', '4. Schedule a trip', '5. Exit']:
            self._output(line)

    def invalid_choice(self) -> None:
        self._output('Invalid option. Choose 1, 2, 3, 4, or 5.')

    def error(self, operation: str, error: Exception) -> None:
        self._output(f'{operation} failed: {error}')

    def available_trips(self, advertisements: Iterable[TripAdvertisement]) -> None:
        advertisements = list(advertisements)
        if not advertisements:
            self._output('No trips have available seats.')
            return
        self._output('Trips with available seats:')
        for ad in advertisements:
            self._output(f'{ad.trip_number}: {ad.departure_time:%Y-%m-%d %H:%M}, '
                         f'{ad.available_seats} seats available')

    def booking(self, result: BookSeatOutputDTO) -> None:
        self._output(f'Booking successful. Booking ID: {result.booking_id}. '
                     f'Advertisement: {result.advertisement_outcome}')

    def trip(self, trip: Trip) -> None:
        self._output(f'Trip {trip.trip_number}: departure {trip.departure_time:%Y-%m-%d %H:%M}, '
                     f'bus {trip.bus.bus_number}, {trip.available_seats}/{trip.capacity} seats available')

    def scheduled(self, trip_number: str) -> None:
        self._output(f'Trip {trip_number} scheduled successfully.')
