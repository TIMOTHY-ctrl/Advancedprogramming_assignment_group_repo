from collections.abc import Callable
from datetime import datetime

from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO
from src.application.Ports.ConsoleUseCases import (
    BookSeatUseCase,
    CreateTripUseCase,
    GetTripUseCase,
    ListAvailableTripsUseCase,
)
from src.Domain.Entities.bus import Bus


class ConsoleApp:
    def __init__(
        self,
        book_seat_service: BookSeatUseCase,
        create_trip_service: CreateTripUseCase,
        get_trip_service: GetTripUseCase,
        list_available_trips_service: ListAvailableTripsUseCase,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._book_seat_service = book_seat_service
        self._create_trip_service = create_trip_service
        self._get_trip_service = get_trip_service
        self._list_available_trips_service = list_available_trips_service
        self._input = input_fn
        self._output = output_fn

    def run(self) -> None:
        while True:
            self._output("")
            self._output("1. Show trips with available seats")
            self._output("2. Book a seat")
            self._output("3. Retrieve a trip")
            self._output("4. Schedule a trip")
            self._output("5. Exit")
            choice = self._input("Select an option: ").strip()

            if choice == "1":
                self._show_available_trips()
            elif choice == "2":
                self._book_seat()
            elif choice == "3":
                self._retrieve_trip()
            elif choice == "4":
                self._create_trip()
            elif choice == "5":
                return
            else:
                self._output("Invalid option. Choose 1, 2, 3, 4, or 5.")

    def _show_available_trips(self) -> None:
        advertisements = self._list_available_trips_service.execute()
        if not advertisements:
            self._output("No trips have available seats.")
            return

        self._output("Trips with available seats:")
        for advertisement in advertisements:
            self._output(
                f"{advertisement.trip_number}: "
                f"{advertisement.departure_time:%Y-%m-%d %H:%M}, "
                f"{advertisement.available_seats} seats available"
            )

    def _book_seat(self) -> None:
        trip_number = self._input("Enter trip number: ").strip()
        passenger_name = self._input("Enter passenger name: ").strip()
        seat_text = self._input("Enter seat number: ").strip()
        try:
            request = BookSeatInputDTO(
                trip_number=trip_number,
                passenger_name=passenger_name,
                seat_number=int(seat_text),
            )
            result = self._book_seat_service.execute(request)
        except ValueError as error:
            self._output(f"Booking failed: {error}")
            return

        self._output(
            f"Booking successful. Booking ID: {result.booking_id}. "
            f"Advertisement: {result.advertisement_outcome}"
        )

    def _retrieve_trip(self) -> None:
        trip_number = self._input("Enter trip number: ").strip()
        try:
            trip = self._get_trip_service.execute(trip_number)
        except ValueError as error:
            self._output(f"Trip lookup failed: {error}")
            return

        self._output(
            f"Trip {trip.trip_number}: "
            f"departure {trip.departure_time:%Y-%m-%d %H:%M}, "
            f"bus {trip.bus.bus_number}, "
            f"{trip.available_seats}/{trip.capacity} seats available"
        )

    def _create_trip(self) -> None:
        trip_number = self._input("Enter trip number: ").strip()
        bus_number = self._input("Enter bus number: ").strip()
        capacity_text = self._input("Enter bus capacity: ").strip()
        departure_text = self._input(
            "Enter departure date and time (YYYY-MM-DD HH:MM): "
        ).strip()
        try:
            bus = Bus(bus_number, int(capacity_text))
            departure_time = datetime.fromisoformat(departure_text)
            trip = self._create_trip_service.execute(
                trip_number, departure_time, bus
            )
        except ValueError as error:
            self._output(f"Trip creation failed: {error}")
            return

        self._output(f"Trip {trip.trip_number} scheduled successfully.")