from datetime import datetime
from src.Domain.Services.BusSchedulingPolicy import BusSchedulingPolicy

from src.Domain.Entities.bus import Bus
from src.Infrastructure.InMemoryTripAdvertisementRepository import (
    InMemoryTripAdvertisementRepository,
)
from src.Infrastructure.InMemoryTripRepository import InMemoryTripRepository
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


def build_console_app() -> ConsoleApp:
    trip_repository = InMemoryTripRepository()
    advertisement_repository = InMemoryTripAdvertisementRepository()

    fully_booked_handler = TripFullyBookedHandler(advertisement_repository)
    advertisement_service = UpdateAdvertisementService(
        advertisement_repository, fully_booked_handler
    )
    create_trip_service = CreateTripService(
        trip_repository, advertisement_service, BusSchedulingPolicy()
    )
    book_seat_service = BookSeatService(
        trip_repository, advertisement_service
    )
    get_trip_service = GetTripService(trip_repository)
    list_available_trips_service = ListAvailableTripsService(
        advertisement_repository
    )

    create_trip_service.execute(
        "TR001",
        datetime.now(),
        Bus(bus_number="BUS001", capacity=3),
    )

    return ConsoleApp(
        book_seat_service=book_seat_service,
        create_trip_service=create_trip_service,
        get_trip_service=get_trip_service,
        list_available_trips_service=list_available_trips_service,
    )


if __name__ == "__main__":
    build_console_app().run()
