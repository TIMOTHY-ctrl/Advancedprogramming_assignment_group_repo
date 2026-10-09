import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier
from unittest.mock import patch

from repository_double import ReferenceTripRepository
from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Entities.bus import Bus
from src.Domain.Services.BusSchedulingPolicy import BusSchedulingPolicy
from src.Domain.ValueObject.seatnumber import SeatNumber
from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.Infrastructure.InMemoryStore import InMemoryStore
from src.Infrastructure.InMemoryUnitOfWork import InMemoryUnitOfWork
from src.Infrastructure.InMemoryTripRepository import InMemoryTripRepository
from src.Infrastructure.InMemoryTripAdvertisementRepository import InMemoryTripAdvertisementRepository
from src.application.DTOs.AdvertisementOutcome import AdvertisementOutcome, AdvertisementStatus, RejectionReason
from src.application.DTOs.BookSeatInputDTO import BookSeatInputDTO
from src.application.EventHandlers.TripFullyBookedHandler import TripFullyBookedHandler
from src.application.UseCases.UpdateAdvertisementService import UpdateAdvertisementService
from src.application.UseCases.CreateTripService import CreateTripService
from src.application.UseCases.BookSeatService import BookSeatService
from src.application.UseCases.GetTripService import GetTripService
from src.application.UseCases.ListAvailableTripsService import ListAvailableTripsService
from src.interface.ConsoleApp import ConsoleApp
from src.interface.ConsoleView import ConsoleView


class BookingArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryStore()
        self.uow = InMemoryUnitOfWork(self.store)
        self.trips = InMemoryTripRepository(self.store)
        self.ads = InMemoryTripAdvertisementRepository(self.store)
        self.handler = TripFullyBookedHandler(self.ads, self.uow)
        self.updates = UpdateAdvertisementService(self.ads, self.handler, self.uow)
        self.create = CreateTripService(self.trips, self.updates, BusSchedulingPolicy(), self.uow)
        self.book = BookSeatService(self.trips, self.updates, self.uow)
        self.time = datetime(2026, 10, 10, 9, 0)
        self.trip = self.create.execute('TR001', self.time, Bus('BUS001', 2))

    def parallel(self, actions):
        gate = Barrier(len(actions))
        def run(action):
            gate.wait(timeout=5)
            try:
                return action()
            except ValueError as error:
                return error
        with ThreadPoolExecutor(max_workers=len(actions)) as pool:
            return list(pool.map(run, actions))

    def test_T1_BR1_positive_integer_seat_value(self):
        self.assertEqual(SeatNumber(1), SeatNumber(1))
        self.assertEqual(int(SeatNumber(1)), 1)
        for value in [0, -1, True, 1.5, '1']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                SeatNumber(value)
        with self.assertRaises(ValueError):
            self.trip.book_seat('Alex', 0)
        with self.assertRaises(ValueError):
            AdvertisementOutcome(AdvertisementStatus.REJECTED)

    def test_T2_BR2_booking_changes_identified_trip_state(self):
        result = self.book.execute(BookSeatInputDTO('TR001', 'Alex', 1))
        saved = self.trips.find_by_number('TR001')
        self.assertEqual(saved.available_seats, 1)
        self.assertEqual(saved.booked_seats[1].booking_id, result.booking_id)
        self.assertEqual(self.trip, saved)  # Identity remains the same despite state changes.
        self.assertEqual(hash(self.trip), hash(saved))
        saved.book_seat('Sam', SeatNumber(2))
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 1)
        self.trips.save(saved)
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 0)
        self.assertEqual(self.trip.available_seats, 2)  # add() also detached its input.
        with self.assertRaises(TypeError):
            saved.booked_seats[3] = saved.booked_seats[1]

    def test_T3_BR3_unique_seats_and_capacity_boundary(self):
        self.book.execute(BookSeatInputDTO('TR001', 'Alex', 2))
        for seat in [2, 3]:
            with self.subTest(seat=seat), self.assertRaises(ValueError):
                self.book.execute(BookSeatInputDTO('TR001', 'Sam', seat))
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 1)
        with self.assertRaises(ValueError):
            self.book.execute(BookSeatInputDTO('TR001', '  ', 1))
        results = self.parallel([
            lambda: self.book.execute(BookSeatInputDTO('TR001', 'Sam', 1)),
            lambda: self.book.execute(BookSeatInputDTO('TR001', 'Jo', 1)),
        ])
        self.assertEqual(sum(isinstance(r, ValueError) for r in results), 1)
        saved = self.trips.find_by_number('TR001')
        self.assertEqual(saved.available_seats, 0)
        self.assertEqual(len(saved.booked_seats), 2)
        self.assertFalse(self.ads.find_by_number('TR001').active)

    def test_T4_BR4_bus_cannot_depart_on_two_trips_at_same_time(self):
        with self.assertRaisesRegex(ValueError, 'already scheduled'):
            self.create.execute('TR002', self.time, Bus('BUS001', 2))
        self.assertIsNone(self.trips.find_by_number('TR002'))
        other = self.create.execute('TR003', self.time, Bus('BUS002', 2))
        self.assertEqual(other.trip_number, 'TR003')
        results = self.parallel([
            lambda: self.create.execute('RACE1', self.time, Bus('BUS003', 2)),
            lambda: self.create.execute('RACE2', self.time, Bus('BUS003', 2)),
        ])
        self.assertEqual(sum(isinstance(r, ValueError) for r in results), 1)
        departures = self.trips.find_departures('BUS003', self.time)
        self.assertEqual(len(departures), 1)
        loser = 'RACE2' if departures[0].trip_number == 'RACE1' else 'RACE1'
        self.assertIsNone(self.ads.find_by_number(loser))

    def test_T5_BR5_final_booking_requests_advertisement_withdrawal(self):
        _, first_event = self.trip.book_seat('Alex', SeatNumber(1))
        _, final_event = self.trip.book_seat('Sam', SeatNumber(2))
        self.assertIsNone(first_event)
        self.assertEqual(final_event, TripFullyBooked('TR001'))
        class RecordingUpdater:
            def __init__(self):
                self.events = []
            def refresh(self, trip, event=None):
                self.events.append(event)
                return AdvertisementOutcome(AdvertisementStatus.ADVERTISED)
        recorder = RecordingUpdater()  # Structural polymorphism, no subclass required.
        BookSeatService(self.trips, recorder, self.uow).execute(BookSeatInputDTO('TR001', 'Jo', 1))
        self.assertEqual(recorder.events, [None])
        class RecordingHandler:
            def handle(self, event):
                self.event = event
                return AdvertisementOutcome(AdvertisementStatus.WITHDRAWN)
        handler = RecordingHandler()
        result = UpdateAdvertisementService(self.ads, handler, self.uow).refresh(self.trip, final_event)
        self.assertEqual(handler.event, final_event)
        self.assertIs(result.status, AdvertisementStatus.WITHDRAWN)

    def test_T6_BR6_existing_trip_required_before_booking(self):
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            self.book.execute(BookSeatInputDTO('MISSING', 'Alex', 1))
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.create.execute('TR001', self.time, Bus('BUS002', 2))
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 2)
        # The same behavioural contract runs against two independent adapters.
        for adapter in [InMemoryTripRepository, ReferenceTripRepository]:
            with self.subTest(adapter=adapter.__name__):
                store = InMemoryStore()
                repository = adapter(store)
                original = Trip('CONTRACT', self.time, Bus('B', 2))
                repository.add(original)
                with self.assertRaises(ValueError):
                    repository.add(original)
                with self.assertRaises(ValueError):
                    repository.add(Trip('CONFLICT', self.time, Bus('B', 2)))
                with self.assertRaises(ValueError):
                    repository.save(Trip('UNKNOWN', self.time, Bus('C', 2)))
                self.assertIsNone(repository.find_by_number('UNKNOWN'))
                loaded = repository.find_by_number(trip_number='CONTRACT')
                loaded.book_seat('Alex', SeatNumber(1))
                self.assertEqual(repository.find_by_number('CONTRACT').available_seats, 2)
                repository.save(loaded)
                self.assertEqual(repository.find_by_number('CONTRACT').available_seats, 1)
                self.assertEqual(len(repository.find_departures('B', self.time)), 1)
                listed = repository.list_all()[0]
                listed.book_seat('Uncommitted', SeatNumber(2))
                self.assertEqual(repository.find_by_number('CONTRACT').available_seats, 1)
                with self.assertRaises(ValueError):
                    repository.save(Trip('CONTRACT', self.time, Bus('B', 3)))
                ads = InMemoryTripAdvertisementRepository(store)
                uow = InMemoryUnitOfWork(store)
                updater = UpdateAdvertisementService(ads, TripFullyBookedHandler(ads, uow), uow)
                updater.refresh(loaded)
                output = BookSeatService(repository, updater, uow).execute(BookSeatInputDTO('CONTRACT', 'Sam', 2))
                self.assertIs(output.advertisement_outcome.status, AdvertisementStatus.WITHDRAWN)
                self.assertEqual(repository.find_by_number('CONTRACT').available_seats, 0)

    def test_T7_main_use_case_handles_event_and_changes_aggregate_B(self):
        results = self.parallel([
            lambda: self.book.execute(BookSeatInputDTO('TR001', 'Alex', 1)),
            lambda: self.book.execute(BookSeatInputDTO('TR001', 'Sam', 2)),
        ])
        self.assertFalse(any(isinstance(r, Exception) for r in results))
        self.assertEqual(sum(r.advertisement_outcome.status is AdvertisementStatus.WITHDRAWN for r in results), 1)
        ad = self.ads.find_by_number('TR001')
        self.assertFalse(ad.active)
        self.assertEqual(ad.available_seats, 0)
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 0)
        self.assertEqual(self.ads.list_available(), [])
        # View/controller integration checks stay in the eight required scenarios.
        prompts = iter(['bad', '3', 'TR001', '4', 'NEW', 'OTHER', '2',
                        '2026-10-11 09:00', '2', 'NEW', 'Jo', 'bad',
                        '2', 'NEW', 'Jo', '1', '1', '5'])
        output = []
        ConsoleApp(self.book, self.create, GetTripService(self.trips),
                   ListAvailableTripsService(self.ads),
                   view=ConsoleView(input_fn=lambda prompt: next(prompts),
                                    output_fn=output.append)).run()
        for expected in ['Invalid option', 'Trip TR001:', 'Trip NEW scheduled',
                         'Booking failed:', 'Booking successful.', 'NEW:']:
            self.assertTrue(any(expected in line for line in output), expected)

    def test_T8_aggregate_B_rejects_repeated_follow_up(self):
        self.book.execute(BookSeatInputDTO('TR001', 'Alex', 1))
        original_save = self.trips.save
        def fail_trip_save(trip):
            original_save(trip)
            raise OSError('trip save failed')
        with patch.object(self.trips, 'save', side_effect=fail_trip_save):
            with self.assertRaisesRegex(OSError, 'trip save failed'):
                self.book.execute(BookSeatInputDTO('TR001', 'Sam', 2))
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 1)
        self.assertEqual(self.ads.find_by_number('TR001').available_seats, 1)
        # An exception AFTER writing B must undo the final booking and B write.
        original_put = self.ads.put
        def fail_after_write(ad):
            original_put(ad)
            raise OSError('simulated storage failure')
        with patch.object(self.ads, 'put', side_effect=fail_after_write):
            with self.assertRaisesRegex(OSError, 'storage failure'):
                self.book.execute(BookSeatInputDTO('TR001', 'Sam', 2))
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 1)
        self.assertTrue(self.ads.find_by_number('TR001').active)
        self.assertEqual(self.ads.find_by_number('TR001').available_seats, 1)
        # Scheduling rollback includes its unique departure index.
        with patch.object(self.ads, 'put', side_effect=fail_after_write):
            with self.assertRaises(OSError):
                self.create.execute('FAIL', self.time, Bus('FAILBUS', 2))
        self.assertIsNone(self.trips.find_by_number('FAIL'))
        self.assertIsNone(self.ads.find_by_number('FAIL'))
        self.assertEqual(self.trips.find_departures('FAILBUS', self.time), [])
        self.create.execute('RETRY', self.time, Bus('FAILBUS', 2))
        self.book.execute(BookSeatInputDTO('TR001', 'Sam', 2))
        before = self.ads.find_by_number('TR001')
        outcome = self.handler.handle(TripFullyBooked('TR001'))
        after = self.ads.find_by_number('TR001')  # Fresh stored state, not a stale snapshot.
        self.assertIs(outcome.status, AdvertisementStatus.REJECTED)
        self.assertIs(outcome.reason, RejectionReason.ALREADY_WITHDRAWN)
        self.assertEqual((after.active, after.available_seats), (before.active, before.available_seats))
        self.assertEqual(self.trips.find_by_number('TR001').available_seats, 0)
        self.assertNotIn('TR001', [ad.trip_number for ad in self.ads.list_available()])
        missing = self.handler.handle(TripFullyBooked('MISSING'))
        self.assertIs(missing.reason, RejectionReason.MISSING)
        self.assertIsNone(self.ads.find_by_number('MISSING'))


if __name__ == '__main__':
    unittest.main()
