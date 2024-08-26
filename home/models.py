from django.db import models

class HotelBooking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE, related_name = "bookings")
    booking_user = models.ForeignKey(HotelUser, on_delete = models.CASCADE,)
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    price = models.FloatField()
