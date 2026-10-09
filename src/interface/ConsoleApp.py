from datetime import datetime
from src.Domain.Entities.bus import Bus
from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO
from src.application.Ports.ConsoleUseCases import (
    BookSeatUseCase, CreateTripUseCase, GetTripUseCase, ListAvailableTripsUseCase,
)
from src.interface.ConsolePresenter import ConsolePresenter


class ConsoleApp:
    """Thin controller: parse input, call a use case, select a view response."""

    def __init__(self, book_seat_service: BookSeatUseCase,
                 create_trip_service: CreateTripUseCase, get_trip_service: GetTripUseCase,
                 list_available_trips_service: ListAvailableTripsUseCase,
                 view: ConsolePresenter) -> None:
        self._book_seat_service = book_seat_service
        self._create_trip_service = create_trip_service
        self._get_trip_service = get_trip_service
        self._list_available_trips_service = list_available_trips_service
        self._view = view

    def run(self) -> None:
        actions = {'1': self._show_available_trips, '2': self._book_seat,
                   '3': self._retrieve_trip, '4': self._create_trip}
        while True:
            self._view.menu()
            try:
                choice = self._view.read('Select an option: ')
                if choice == '5':
                    return
                action = actions.get(choice)
                if action is None:
                    self._view.invalid_choice()
                else:
                    action()
            except EOFError:
                return

    def _show_available_trips(self) -> None:
        try:
            self._view.available_trips(self._list_available_trips_service.execute())
        except OSError as error:
            self._view.error('Trip listing', error)

    def _book_seat(self) -> None:
        number = self._view.read('Enter trip number: ')
        name = self._view.read('Enter passenger name: ')
        seat = self._view.read('Enter seat number: ')
        try:
            result = self._book_seat_service.execute(BookSeatInputDTO(number, name, int(seat)))
        except (ValueError, OSError) as error:
            self._view.error('Booking', error)
            return
        self._view.booking(result)

    def _retrieve_trip(self) -> None:
        number = self._view.read('Enter trip number: ')
        try:
            trip = self._get_trip_service.execute(number)
        except (ValueError, OSError) as error:
            self._view.error('Trip lookup', error)
            return
        self._view.trip(trip)

    def _create_trip(self) -> None:
        number = self._view.read('Enter trip number: ')
        bus_number = self._view.read('Enter bus number: ')
        capacity = self._view.read('Enter bus capacity: ')
        departure = self._view.read('Enter departure date and time (YYYY-MM-DD HH:MM): ')
        try:
            trip = self._create_trip_service.execute(
                number, datetime.fromisoformat(departure), Bus(bus_number, int(capacity)))
        except (ValueError, OSError) as error:
            self._view.error('Trip creation', error)
            return
        self._view.scheduled(trip.trip_number)
