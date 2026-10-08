import unittest
from datetime import datetime

from src.Domain.Entities.bus import Bus
from src.Infrastructure.InMemoryTripAdvertisementRepository import (
    InMemoryTripAdvertisementRepository,
)
from src.Infrastructure.InMemoryTripRepository import InMemoryTripRepository
from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO
from src.application.EventHandlers.TripFullyBookedHandler import (
    TripFullyBookedHandler,
)
from src.application.UseCases.BookSeatService import BookSeatService
from src.application.UseCases.CreateTripService import CreateTripService
from src.application.UseCases.GetTripService import GetTripService
from src.application.UseCases.ListAvailableTripsService import (
    ListAvailableTripsService,
)
from src.application.UseCases.UpdateAdvertisementService import (
    UpdateAdvertisementService,
)
from src.interface.ConsoleApp import ConsoleApp


class BookingArchitectureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.trip_repository = InMemoryTripRepository()
        self.advertisement_repository = InMemoryTripAdvertisementRepository()
        self.fully_booked_handler = TripFullyBookedHandler(
            self.advertisement_repository
        )
        self.advertisement_service = UpdateAdvertisementService(
            self.advertisement_repository, self.fully_booked_handler
        )
        self.create_trip_service = CreateTripService(
            self.trip_repository, self.advertisement_service
        )
        self.book_seat_service = BookSeatService(
            self.trip_repository,
            self.advertisement_service,
        )
        self.departure_time = datetime(2026, 10, 9, 18, 0)
        self.trip = self.create_trip_service.execute(
            "TR001", self.departure_time, Bus("BUS001", 2)
        )

    def test_created_trip_is_retrievable_and_advertised(self) -> None:
        trip = GetTripService(self.trip_repository).execute("TR001")

        self.assertIs(trip, self.trip)
        self.assertEqual(trip.departure_time, self.departure_time)
        self.assertEqual(trip.capacity, 2)
        advertisement = ListAvailableTripsService(
            self.advertisement_repository
        ).execute()[0]
        self.assertEqual(advertisement.trip_number, "TR001")
        self.assertEqual(advertisement.available_seats, 2)

    def test_duplicate_trip_number_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.create_trip_service.execute(
                "TR001", self.departure_time, Bus("BUS002", 2)
            )

    def test_booking_same_seat_twice_is_rejected(self) -> None:
        request = BookSeatInputDTO("TR001", "Alex", 1)
        self.book_seat_service.execute(request)

        with self.assertRaisesRegex(ValueError, "already booked"):
            self.book_seat_service.execute(
                BookSeatInputDTO("TR001", "Sam", 1)
            )

    def test_full_trip_is_withdrawn_from_advertisements(self) -> None:
        first = self.book_seat_service.execute(
            BookSeatInputDTO("TR001", "Alex", 1)
        )
        self.assertEqual(first.available_seats, 1)
        self.assertEqual(
            self.advertisement_repository.list_available()[0].available_seats,
            1,
        )

        self.book_seat_service.execute(BookSeatInputDTO("TR001", "Sam", 2))

        self.assertEqual(self.advertisement_repository.list_available(), [])
        with self.assertRaisesRegex(ValueError, "fully booked"):
            self.book_seat_service.execute(
                BookSeatInputDTO("TR001", "Taylor", 1)
            )

    def test_seat_must_be_within_bus_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 1 and 2"):
            self.book_seat_service.execute(
                BookSeatInputDTO("TR001", "Alex", 3)
            )

    def test_console_can_retrieve_a_trip_and_exit(self) -> None:
        prompts = iter(["3", "TR001", "5"])
        output: list[str] = []
        app = ConsoleApp(
            book_seat_service=self.book_seat_service,
            create_trip_service=self.create_trip_service,
            get_trip_service=GetTripService(self.trip_repository),
            list_available_trips_service=ListAvailableTripsService(
                self.advertisement_repository
            ),
            input_fn=lambda prompt: (output.append(prompt), next(prompts))[1],
            output_fn=output.append,
        )

        app.run()

        self.assertTrue(any("Trip TR001:" in line for line in output))

    def test_console_can_schedule_a_trip(self) -> None:
        prompts = iter(
            [
                "4",
                "TR002",
                "BUS002",
                "4",
                "2026-10-10 09:30",
                "5",
            ]
        )
        output: list[str] = []
        app = ConsoleApp(
            book_seat_service=self.book_seat_service,
            create_trip_service=self.create_trip_service,
            get_trip_service=GetTripService(self.trip_repository),
            list_available_trips_service=ListAvailableTripsService(
                self.advertisement_repository
            ),
            input_fn=lambda prompt: (output.append(prompt), next(prompts))[1],
            output_fn=output.append,
        )

        app.run()

        self.assertIsNotNone(
            self.trip_repository.find_by_number("TR002")
        )
        self.assertTrue(
            any("Trip TR002 scheduled successfully." == line for line in output)
        )


if __name__ == "__main__":
    unittest.main()
