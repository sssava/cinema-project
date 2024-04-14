from django.db import models
from django.contrib.auth import get_user_model
from .managers import SessionManager

User = get_user_model()


class AbstractPerson(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        abstract = True


class Director(AbstractPerson):
    class Meta:
        db_table = "director"


class Actor(AbstractPerson):
    class Meta:
        db_table = "actor"


class Genre(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'genre'

    def __str__(self):
        return f"{self.name}"


class Movie(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='movies/')
    rating = models.FloatField()
    genres = models.ManyToManyField(Genre, through="MovieGenre")
    directors = models.ManyToManyField(Director, through="MovieDirector")
    actors = models.ManyToManyField(Actor, through="MovieActor")

    class Meta:
        db_table = 'movie'

    def __str__(self):
        return f"{self.name}"


class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_genre')
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING, related_name='movie_genre')

    class Meta:
        db_table = 'movie_genre'

    def __str__(self):
        return f"{self.movie.name} - {self.genre.name}"


class MovieDirector(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_director')
    director = models.ForeignKey(Director, on_delete=models.DO_NOTHING, related_name='movie_director')

    class Meta:
        db_table = 'movie_director'

    def __str__(self):
        return f"{self.movie.name} - {self.director.name}"


class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_actor')
    actor = models.ForeignKey(Actor, on_delete=models.DO_NOTHING, related_name='movie_actor')

    class Meta:
        db_table = 'movie_actor'

    def __str__(self):
        return f"{self.movie.name} - {self.actor.name}"


class MovieHall(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_per_row = models.IntegerField()

    class Meta:
        db_table = 'movieHall'

    def __str__(self):
        return f"Name: {self.name}, Rows: {self.rows}, Seats per row: {self.seats_per_row}"

    def create_seats_for_hall(self):
        seats = []
        for row in range(1, self.rows + 1):
            for seat in range(1, self.seats_per_row + 1):
                seats.append(Seat(row_number=row, seat_number=seat, hall=self))
        Seat.objects.bulk_create(seats)

    def is_updateble_hall(self):
        sessions = Session.objects.filter(hall=self)
        if sessions:
            for session in sessions:
                if session.session_seats.filter(is_booked=True).exists():
                    return False
            return True
        return True

    def delete_seats_and_session_seats(self):
        if self.is_updateble_hall():
            self.seats.filter(hall=self).delete()

    def update_seats_for_hall(self):
        self.create_seats_for_hall()
        for session in self.sessions.all():
            session.create_session_seats()


class Seat(models.Model):
    row_number = models.IntegerField()
    seat_number = models.IntegerField()
    hall = models.ForeignKey(MovieHall, on_delete=models.DO_NOTHING, related_name='seats')

    class Meta:
        db_table = 'seat'

    def __str__(self):
        return f"Row number: {self.row_number}, Seat number: {self.seat_number}, in Hall - {self.hall.name}"


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT, related_name="sessions")
    time_start = models.TimeField()
    time_end = models.TimeField()
    date_start = models.DateField()
    date_end = models.DateField()
    session_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hall = models.ForeignKey(MovieHall, models.PROTECT, related_name='sessions')

    objects = SessionManager()

    class Meta:
        db_table = "session"

    def __str__(self):
        return f"Movie: {self.movie.name}, price: {self.price}, in hall: {self.hall.name}"

    @property
    def get_available_seats(self):
        return SessionSeat.objects.filter(session=self, is_booked=False).count()

    def create_session_seats(self):
        session_seats = []
        hall = self.hall
        seats = Seat.objects.filter(hall=hall).order_by('pk')
        for seat in seats:
            session_seats.append(SessionSeat(session=self, seat=seat))
        SessionSeat.objects.bulk_create(session_seats)

    def is_updateble_session(self):
        return not self.session_seats.filter(is_booked=True).exists()

    def delete_session_seats(self):
        if self.is_updateble_session():
            self.session_seats.all().delete()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="orders")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = "order"

    def __str__(self):
        return f"User: {self.user.username}, purchase_price: {self.purchase_price}"


class SessionSeat(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, related_name="session_seats")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="session_seats")
    is_booked = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name="session_seats", blank=True, null=True)

    class Meta:
        db_table = "session_seat"

    def __str__(self):
        return f"Row - {self.seat.row_number}, Seat - {self.seat.seat_number}"




