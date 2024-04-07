from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MovieHall, Seat, Session, SessionSeat


@receiver(post_save, sender=MovieHall)
def create_seats_for_hall(sender, instance, created, **kwargs):
    if created:
        seats = []
        for row in range(1, instance.rows + 1):
            for seat in range(1, instance.seats_per_row + 1):
                seats.append(Seat(row_number=row, seat_number=seat, hall=instance))
        Seat.objects.bulk_create(seats)


@receiver(post_save, sender=Session)
def create_session_seats(sender, instance, created, **kwargs):
    if created:
        session_seats = []
        hall = instance.hall
        seats = Seat.objects.filter(hall=hall).order_by('pk')
        for seat in seats:
            session_seats.append(SessionSeat(session=instance, seat=seat))
        SessionSeat.objects.bulk_create(session_seats)
