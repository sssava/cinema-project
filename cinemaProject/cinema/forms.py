from django import forms
from cinema.models import MovieHall


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
