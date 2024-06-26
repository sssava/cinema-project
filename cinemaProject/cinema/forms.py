from datetime import date, time, datetime
from django.db.models import Q
from django import forms
from cinema.models import MovieHall, Session


class MovieHallCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(
            attrs={'class': 'form-control input-md', 'placeholder': 'Enter hall name'}
        )
        self.fields['rows'].widget = forms.NumberInput(
            attrs={'class': 'form-control input-md', 'placeholder': 'Enter hall rows'}
        )
        self.fields['seats_per_row'].widget = forms.NumberInput(
            attrs={'class': 'form-control input-md', 'placeholder': 'Enter hall seats per row'}
        )

    class Meta:
        model = MovieHall
        fields = "__all__"

    error_messages = {
        "invalid_count": "Count should be bigger than 0",
        "name_exists": "Hall with that name already exists"
    }

    def clean_rows(self):
        rows = self.cleaned_data['rows']
        if rows <= 0:
            raise forms.ValidationError(
                self.error_messages["invalid_count"],
                code="invalid_count",
            )

        return rows

    def clean_seats_per_row(self):
        seats_per_row = self.cleaned_data['seats_per_row']
        if seats_per_row <= 0:
            raise forms.ValidationError(
                self.error_messages["invalid_count"],
                code="invalid_count",
            )

        return seats_per_row

    def clean_name(self):
        name = self.cleaned_data['name']
        if MovieHall.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(
                self.error_messages["name_exists"],
                code="name_exists"
            )
        return name


class MovieHallUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(
            attrs={'class': 'form-control input-md', 'placeholder': 'Enter hall name'}
        )
        self.fields['rows'].widget = forms.NumberInput(
            attrs={'class': 'form-control input-md', 'placeholder': 'Enter hall rows'}
        )
        self.fields['seats_per_row'].widget = forms.NumberInput(
            attrs={'class': 'form-control input-md', 'placeholder': 'Enter hall seats per row'}
        )

    class Meta:
        model = MovieHall
        fields = "__all__"

    error_messages = {
        "invalid_count": "Count should be bigger than 0",
        "name_exists": "Hall with that name already exists"
    }

    def clean_rows(self):
        rows = self.cleaned_data['rows']
        if rows <= 0:
            raise forms.ValidationError(
                self.error_messages["invalid_count"],
                code="invalid_count",
            )

        return rows

    def clean_seats_per_row(self):
        seats_per_row = self.cleaned_data['seats_per_row']
        if seats_per_row <= 0:
            raise forms.ValidationError(
                self.error_messages["invalid_count"],
                code="invalid_count",
            )

        return seats_per_row

    def clean_name(self):
        name = self.cleaned_data['name']
        if MovieHall.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                self.error_messages["name_exists"],
                code="name_exists"
            )
        return name


class SessionFormBase(forms.ModelForm):
    error_messages = {
        "invalid_date": "session date should be between start date and end date",
        "invalid_session": "session on this time in that hall already exists",
        "invalid_price": "price should be bigger than 0",
        "invalid_time": "invalid format time"
    }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError(
                self.error_messages['invalid_price'],
                code='invalid_price'
            )
        return price

    def is_session_date_between(self, session_date, date_start, date_end):
        if isinstance(session_date, date) and isinstance(date_start, date) and isinstance(date_end, date):
            if not (date_start <= session_date <= date_end):
                raise forms.ValidationError(
                    self.error_messages['invalid_date'],
                    code='invalid_date'
                )

    def clean_session_time(self, time_start, time_end, session_date, hall, session_pk=None):
        if isinstance(time_start, time) and isinstance(time_end, time):
            if (Session.objects.exists_session_by_time(time_end, session_date, hall, session_pk)
                    or Session.objects.exists_session_by_time(time_start, session_date, hall, session_pk)):
                raise forms.ValidationError(
                    self.error_messages['invalid_session'],
                    code='invalid_session'
                )
        else:
            raise forms.ValidationError(
                self.error_messages['invalid_time'],
                code="invalid_time"
            )


class SessionCreationForm(SessionFormBase):
    class Meta:
        model = Session
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        session_date = cleaned_data.get('session_date')
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')
        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')
        hall = cleaned_data['hall']
        self.is_session_date_between(session_date, date_start, date_end)
        self.clean_session_time(time_start, time_end, session_date, hall)


class SessionUpdateForm(SessionFormBase):
    class Meta:
        model = Session
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        session_date = cleaned_data.get('session_date')
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')
        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')
        hall = cleaned_data.get('hall')
        instance = self.instance
        self.is_session_date_between(session_date, date_start, date_end)
        self.clean_session_time(time_start, time_end, session_date, hall, session_pk=instance.pk)
