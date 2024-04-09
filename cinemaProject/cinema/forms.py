from datetime import date, time
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
        rows = self.cleaned_data.get('rows')
        if rows <= 0:
            raise forms.ValidationError(
                self.error_messages["invalid_count"],
                code="invalid_count",
            )

        return rows

    def clean_seats_per_row(self):
        seats_per_row = self.cleaned_data.get('seats_per_row')
        if seats_per_row <= 0:
            raise forms.ValidationError(
                self.error_messages["invalid_count"],
                code="invalid_count",
            )

        return seats_per_row

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if MovieHall.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(
                self.error_messages["name_exists"],
                code="name_exists"
            )
        return name


class SessionCreationForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = "__all__"

    error_messages = {
        "invalid_date": "session date should be between start date and end date",
        "invalid_session": "session on this time in that hall already exists",
        "invalid_price": "price should be bigger than 0"
    }

    # def clean_date_start(self):
    #     date_start = self.cleaned_data.get('date_start')
    #     if not isinstance(date_start, datetime):
    #         raise forms.ValidationError(
    #             self.error_messages['invalid_date_format'],
    #             code="invalid_date_format"
    #         )
    #     return date_start
    #
    # def clean_date_end(self):
    #     date_end = self.cleaned_data.get('date_end')
    #     if not isinstance(date_end, datetime):
    #         raise forms.ValidationError(
    #             self.error_messages['invalid_date_format'],
    #             code="invalid_date_format"
    #         )
    #     return date_end
    #
    # def clean_session_date(self):
    #     session_date = self.cleaned_data.get('session_date')
    #     if not isinstance(session_date, datetime):
    #         raise forms.ValidationError(
    #             self.error_messages['invalid_date_format'],
    #             code="invalid_date_format"
    #         )
    #     return session_date

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError(
                self.error_messages['invalid_price'],
                code='invalid_price'
            )

    def clean(self):
        cleaned_data = super().clean()
        session_date = cleaned_data.get('session_date')
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')
        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')
        hall = cleaned_data.get('hall')
        if isinstance(session_date, date) and isinstance(date_start, date) and isinstance(date_end, date):
            if not (date_start <= session_date <= date_end):
                raise forms.ValidationError(
                    self.error_messages['invalid_date'],
                    code='invalid_date'
                )
            exists_sessions_by_time_end = Session.objects.filter(
                Q(time_start__lte=time_end) & Q(time_end__gte=time_end),
                hall=hall,
                session_date=session_date
            ).exists()

            exists_sessions_by_time_start = Session.objects.filter(
                Q(time_start__lte=time_start) & Q(time_end__gte=time_start),
                hall=hall,
                session_date=session_date
            ).exists()

            if exists_sessions_by_time_end or exists_sessions_by_time_start:
                raise forms.ValidationError(
                    self.error_messages['invalid_session'],
                    code='invalid_session'
                )
