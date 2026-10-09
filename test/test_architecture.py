import unittest
from datetime import datetime
from src.Domain.Entities.bus import Bus
from src.Domain.ValueObject.seatnumber import SeatNumber
from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.Infrastructure.InMemoryTripRepository import InMemoryTripRepository
from src.Infrastructure.InMemoryTripAdvertisementRepository import InMemoryTripAdvertisementRepository
from src.application.EventHandlers.TripFullyBookedHandler import TripFullyBookedHandler
from src.application.UseCases.UpdateAdvertisementService import UpdateAdvertisementService
from src.application.UseCases.CreateTripService import CreateTripService
from src.application.UseCases.BookSeatService import BookSeatService
from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO


class BookingArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.trips = InMemoryTripRepository()
        self.ads = InMemoryTripAdvertisementRepository()
        self.handler = TripFullyBookedHandler(self.ads)
        self.updates = UpdateAdvertisementService(self.ads, self.handler)
        self.create = CreateTripService(self.trips, self.updates)
        self.book = BookSeatService(self.trips, self.updates)
        self.time = datetime(2026, 10, 10, 9, 0)
        self.trip = self.create.execute('TR001', self.time, Bus('BUS001', 2))

    def test_T1_BR1_positive_integer_seat_value(self):
        self.assertEqual(SeatNumber(1), SeatNumber(1))
        for value in [0, -1, True, 1.5, '1']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                SeatNumber(value)

    def test_T2_BR2_booking_changes_identified_trip_state(self):
        result = self.book.execute(BookSeatInputDTO('TR001', 'Alex', 1))
        self.assertEqual(self.trip.trip_number, 'TR001')
        self.assertEqual(self.trip.available_seats, 1)
        self.assertEqual(self.trip.booked_seats[1].booking_id, result.booking_id)

    def test_T3_BR3_unique_seats_and_capacity_boundary(self):
        self.book.execute(BookSeatInputDTO('TR001', 'Alex', 2))
        for seat in [2, 3]:
            with self.subTest(seat=seat), self.assertRaises(ValueError):
                self.book.execute(BookSeatInputDTO('TR001', 'Sam', seat))
        self.assertEqual(self.trip.available_seats, 1)
        self.assertEqual(len(self.trip.booked_seats), 1)

    def test_T4_BR4_bus_cannot_depart_on_two_trips_at_same_time(self):
        with self.assertRaisesRegex(ValueError, 'already scheduled'):
            self.create.execute('TR002', self.time, Bus('BUS001', 2))
        self.assertIsNone(self.trips.find_by_number('TR002'))
        other = self.create.execute('TR003', self.time, Bus('BUS002', 2))
        self.assertEqual(other.trip_number, 'TR003')

    def test_T5_BR5_final_booking_requests_advertisement_withdrawal(self):
        _, first_event = self.trip.book_seat('Alex', SeatNumber(1))
        _, final_event = self.trip.book_seat('Sam', SeatNumber(2))
        self.assertIsNone(first_event)
        self.assertEqual(final_event, TripFullyBooked('TR001'))

    def test_T6_BR6_existing_trip_required_before_booking(self):
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            self.book.execute(BookSeatInputDTO('MISSING', 'Alex', 1))
        self.assertEqual(self.trip.available_seats, 2)
        self.assertEqual(len(self.ads.list_available()), 1)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.create.execute('TR001', self.time, Bus('BUS002', 2))

    def test_T7_main_use_case_handles_event_and_changes_aggregate_B(self):
        self.book.execute(BookSeatInputDTO('TR001', 'Alex', 1))
        result = self.book.execute(BookSeatInputDTO('TR001', 'Sam', 2))
        ad = self.ads.find_by_number('TR001')
        self.assertEqual(result.available_seats, 0)
        self.assertEqual(result.advertisement_outcome, 'withdrawn')
        self.assertFalse(ad.active)
        self.assertEqual(ad.available_seats, 0)
        self.assertEqual(self.ads.list_available(), [])

    def test_T8_aggregate_B_rejects_repeated_follow_up(self):
        self.book.execute(BookSeatInputDTO('TR001', 'Alex', 1))
        self.book.execute(BookSeatInputDTO('TR001', 'Sam', 2))
        ad = self.ads.find_by_number('TR001')
        before = (ad.active, ad.available_seats)
        outcome = self.handler.handle(TripFullyBooked('TR001'))
        self.assertEqual(outcome, 'rejected: advertisement already withdrawn')
        self.assertEqual((ad.active, ad.available_seats), before)
        self.assertEqual(self.trip.available_seats, 0)
        self.assertEqual(self.ads.list_available(), [])


if __name__ == '__main__':
    unittest.main()
