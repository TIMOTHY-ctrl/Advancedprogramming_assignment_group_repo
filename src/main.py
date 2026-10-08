from datetime import datetime

from Domain.domain import Bus, BusBookingSystem
from application.application import BookingApplication
from interface.interface import BookingInterface

booking_system = BusBookingSystem()
booking_system.create_trip("TR001", datetime.now(), Bus("BUS001", 3))
application = BookingApplication(booking_system)
interface = BookingInterface(application)
interface.run()