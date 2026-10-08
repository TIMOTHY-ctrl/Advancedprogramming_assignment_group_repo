class BookingInterface:
    def __init__(self, booking_application):
        self.booking_application = booking_application

    def show_available_trips(self):
        trips = self.booking_application.get_available_trips()
        if not trips:
            print("No trips have available seats.")
            return

        print("Trips with available seats:")
        for trip in trips:
            print(
                f"{trip.trip_number}: "
                f"{trip.departure_time:%Y-%m-%d %H:%M}, "
                f"{trip.available_seats} seats available"
            )

    def retrieve_trip(self):
        trip_number = input("Enter trip number: ")
        try:
            trip = self.booking_application.get_trip(trip_number)
        except ValueError as error:
            print(f"Trip lookup failed: {error}")
            return

        print(
            f"Trip {trip.trip_number}: "
            f"departure {trip.departure_time:%Y-%m-%d %H:%M}, "
            f"bus {trip.bus.bus_number}, "
            f"{trip.available_seats}/{trip.capacity} seats available"
        )

    def book_seat(self):
        try:
            trip_number = input("Enter trip number: ")
            passenger_name = input("Enter passenger name: ")
            seat_number = int(input("Enter seat number: "))
            booking_id = self.booking_application.book_seat(
                trip_number,
                passenger_name,
                seat_number
            )
            print(
                f"Booking successful. "
                f"Booking ID: {booking_id}"
            )
        except ValueError as error:
            print(f"Booking failed: {error}")

    def run(self):
        while True:
            print("\n1. Show trips with available seats")
            print("2. Book a seat")
            print("3. Retrieve a trip")
            print("4. Exit")
            choice = input("Select an option: ")

            if choice == "1":
                self.show_available_trips()
            elif choice == "2":
                self.book_seat()
            elif choice == "3":
                self.retrieve_trip()
            elif choice == "4":
                return
            else:
                print("Invalid option.")