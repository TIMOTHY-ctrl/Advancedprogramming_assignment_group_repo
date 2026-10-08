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