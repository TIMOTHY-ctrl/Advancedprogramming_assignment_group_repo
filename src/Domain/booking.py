class Booking:
    def __init__(self,booking_id,passenger_id,passenger_name,phone,seat_number):
        self.booking_id = booking_id
        self.passenger_id = passenger_id
        self.passenger_name = passenger_name
        self.phone = phone
        self.seat_number = seat_number

class Booktrip:
    def save(self, booking_id,passenger_id, passenger_name):

        