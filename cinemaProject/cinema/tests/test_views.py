from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from cinema.factories import (
    MovieHallFactory,
    SessionTodayFactory,
    UserFactory,
    DirectorFactory,
    ActorFactory,
    GenreFactory,
    MovieFactory,
    SessionTomorrowFactory,
    SuperUserFactory,
)
from django.test import override_settings
from django.conf import settings
import os
from cinema.models import Session, MovieHall, Seat, SessionSeat, Order
from unittest.mock import patch
from django.contrib.messages import get_messages
from datetime import time, datetime, timedelta

User = get_user_model()
media_for_tests = os.path.join(settings.BASE_DIR, 'media_for_tests')


class SessionListTests(TestCase):
    @override_settings(MEDIA_ROOT=media_for_tests)
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(user=self.user)
        self.hall = MovieHallFactory()
        self.hall2 = MovieHallFactory()
        self.session = SessionTodayFactory.create(hall=self.hall)
        self.session2 = SessionTodayFactory.create(hall=self.hall2)
        self.session_tomorrow = SessionTomorrowFactory(hall=self.hall2)

    def test_session_list(self):
        url = reverse("index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(list(sessions), [self.session, self.session2])

    def test_session_list_tomorrow(self):
        url = reverse("tomorrow")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(list(sessions), [self.session_tomorrow,])

    def test_session_list_today_pagination(self):
        url = reverse("index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('paginator' in response.context)
        self.assertEqual(response.context['paginator'].num_pages, 1)
        self.assertTrue('sessions' in response.context)
        self.assertEqual(len(response.context['sessions']), 2)


class MovieHallCreationViewTest(TestCase):
    @override_settings(MEDIA_ROOT=media_for_tests)
    def setUp(self):
        self.superuser = SuperUserFactory()
        self.user = UserFactory()
        self.client.force_login(user=self.superuser)
        self.hall = MovieHallFactory()

    def test_form_valid(self):
        form_data = {'name': 'Test Hall', 'rows': 5, 'seats_per_row': 5}
        with patch('cinema.models.MovieHall.create_seats_for_hall') as mock_create_seats:
            response = self.client.post(reverse('create-movie-hall'), data=form_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(MovieHall.objects.count(), 2)
            self.assertTrue(mock_create_seats.called)

    def test_form_invalid_existing_name(self):
        invalid_data = {'name': self.hall.name, 'rows': 5, 'seats_per_row': 10}
        response = self.client.post(reverse('create-movie-hall'), data=invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MovieHall.objects.count(), 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(str(messages[0]), '* name\n  * Hall with that name already exists')

    def test_form_invalid_rows(self):
        invalid_data = {'name': "orange", 'rows': -5, 'seats_per_row': -10}
        response = self.client.post(reverse('create-movie-hall'), data=invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MovieHall.objects.count(), 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')

    def test_create_for_general_user(self):
        self.client.force_login(user=self.user)
        form_data = {'name': 'Test Hall', 'rows': 5, 'seats_per_row': 5}
        with patch('cinema.models.MovieHall.create_seats_for_hall') as mock_create_seats:
            response = self.client.post(reverse('create-movie-hall'), data=form_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, "/no-permission/")
            self.assertEqual(MovieHall.objects.count(), 1)
            mock_create_seats.assert_not_called()


class SessionCreationViewTest(TestCase):
    @override_settings(MEDIA_ROOT=media_for_tests)
    def setUp(self):
        self.superuser = SuperUserFactory()
        self.user = UserFactory()
        self.client.force_login(user=self.superuser)
        self.hall = MovieHallFactory()
        self.movie = MovieFactory()
        self.session = SessionTodayFactory(
            time_start=time(hour=18, minute=20), time_end=time(hour=19, minute=20), hall=self.hall
        )

    def test_form_valid(self):
        form_data = {
            'movie': self.movie.id,
            'time_start': '20:00:00',
            'time_end': '21:00:00',
            'date_start': datetime.now().date(),
            "date_end": datetime.now().date() + timedelta(days=5),
            "session_date": datetime.now().date(),
            "price": "6",
            "hall": self.hall.id,
        }
        response = self.client.post(reverse('create-session'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertEqual(Session.objects.count(), 2)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'success')
        self.assertEqual(str(messages[0]), 'Session has successfully created')

    def test_form_invalid_date(self):
        form_data = {
            'movie': self.movie.id,
            'time_start': '20:00:00',
            'time_end': '21:00:00',
            'date_start': datetime.now().date(),
            "date_end": datetime.now().date() + timedelta(days=5),
            "session_date": datetime.now().date() - timedelta(days=4),
            "price": "6",
            "hall": self.hall.id,
        }

        response = self.client.post(reverse('create-session'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertEqual(Session.objects.count(), 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(str(messages[0]), '* __all__\n  * session date should be between start date and end date')

    def test_form_invalid_price(self):
        form_data = {
            'movie': self.movie.id,
            'time_start': '20:00:00',
            'time_end': '21:00:00',
            'date_start': datetime.now().date(),
            "date_end": datetime.now().date() + timedelta(days=5),
            "session_date": datetime.now().date(),
            "price": "-6",
            "hall": self.hall.id,
        }

        response = self.client.post(reverse('create-session'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertEqual(Session.objects.count(), 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(str(messages[0]), '* price\n  * price should be bigger than 0')

    def test_form_existing_session_time(self):
        form_data = {
            'movie': self.movie.id,
            'time_start': '19:00:00',
            'time_end': '20:00:00',
            'date_start': datetime.now().date(),
            "date_end": datetime.now().date() + timedelta(days=5),
            "session_date": datetime.now().date(),
            "price": "6",
            "hall": self.hall.id,
        }

        response = self.client.post(reverse('create-session'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertEqual(Session.objects.count(), 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(str(messages[0]), '* __all__\n  * session on this time in that hall already exists')

    def test_create_for_general_user(self):
        self.client.force_login(user=self.user)
        form_data = {
            'movie': self.movie.id,
            'time_start': '20:00:00',
            'time_end': '21:00:00',
            'date_start': datetime.now().date(),
            "date_end": datetime.now().date() + timedelta(days=5),
            "session_date": datetime.now().date(),
            "price": "6",
            "hall": self.hall.id,
        }
        response = self.client.post(reverse('create-session'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/no-permission/')
        self.assertEqual(Session.objects.count(), 1)


class SessionDetailViewTests(TestCase):
    @override_settings(MEDIA_ROOT=media_for_tests)
    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory(money=0)
        self.hall = MovieHallFactory()
        self.hall.create_seats_for_hall()
        self.session = SessionTodayFactory(hall=self.hall)
        self.session.create_session_seats()

    def test_session_detail_view(self):
        self.client.force_login(user=self.user)
        url = reverse('session-detail', kwargs={'session_id': self.session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_session_detail_view_logout_user(self):
        url = reverse('session-detail', kwargs={'session_id': self.session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    @patch('cinema.views.is_buying')
    @patch('cinema.views.create_order')
    def test_post_method(self, mock_create_order, mock_is_buying):
        self.client.force_login(user=self.user)
        url = reverse('session-detail', kwargs={'session_id': self.session.id})
        data = {'selected_seats': [self.session.session_seats.first().id]}
        response = self.client.post(url, data)
        self.assertTrue(mock_is_buying.called)
        self.assertTrue(mock_create_order.called)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/session/{self.session.id}/')


class MovieHallUpdateViewTest(TestCase):
    @override_settings(MEDIA_ROOT=media_for_tests)
    def setUp(self):
        self.superuser = SuperUserFactory()
        self.client.force_login(user=self.superuser)
        self.hall = MovieHallFactory()
        self.url = reverse("update-hall", kwargs={"pk": self.hall.pk})
        self.valid_data = {"name": "New Hall Name", "rows": 10, "seats_per_row": 10}
        self.invalid_data = {"name": "", "rows": 10, "seats_per_row": 10}

    def test_form_valid(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertTrue(MovieHall.objects.filter(name="New Hall Name").exists())
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Hall has successfully updated", messages)

    def test_form_invalid(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertFalse(MovieHall.objects.filter(name="New Hall Name").exists())
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("* name\n  * This field is required.", messages)
