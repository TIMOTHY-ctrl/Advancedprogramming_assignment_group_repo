import unittest
from datetime import datetime

from src.Domain.domain import Bus, BusBookingSystem


class BusBookingSystemTests(unittest.TestCase):
    def setUp(self):
        self.system = BusBookingSystem()
        self.bus = Bus("BUS001", 2)
        self.departure_time = datetime(2026, 10, 8, 18, 0)
        self.trip = self.system.create_trip(
            "TR001", self.departure_time, self.bus
        )

    def test_trip_uses_assigned_bus_capacity_and_is_retrievable(self):
        trip = self.system.get_trip("TR001")

        self.assertIs(trip, self.trip)
        self.assertEqual(trip.bus, self.bus)
        self.assertEqual(trip.departure_time, self.departure_time)
        self.assertEqual(trip.capacity, 2)

    def test_duplicate_trip_number_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.system.create_trip("TR001", self.departure_time, self.bus)

    def test_seat_cannot_be_booked_twice_on_same_trip(self):
        self.system.book_seat("TR001", "Alex", 1)

        with self.assertRaisesRegex(ValueError, "already booked"):
            self.system.book_seat("TR001", "Sam", 1)

    def test_full_trip_is_removed_from_available_trips(self):
        self.system.book_seat("TR001", "Alex", 1)
        self.assertEqual(self.system.get_available_trips(), [self.trip])

        self.system.book_seat("TR001", "Sam", 2)

        self.assertEqual(self.trip.available_seats, 0)
        self.assertFalse(self.trip.has_available_seats)
        self.assertEqual(self.system.get_available_trips(), [])
        with self.assertRaisesRegex(ValueError, "fully booked"):
            self.system.book_seat("TR001", "Taylor", 1)

    def test_seat_number_must_be_within_bus_capacity(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 2"):
            self.system.book_seat("TR001", "Alex", 3)

    def test_missing_trip_is_reported(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            self.system.get_trip("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
