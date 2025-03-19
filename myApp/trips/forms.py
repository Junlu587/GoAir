from django import forms
from .models import Trip
from ..flights.models import Flight


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'flight_number',
            'origin',
            'destination',
            'departure_date',
            'status',
            'current_price',  # 将当前价位也放入表单字段
            'return_date',
            'airline_company',
            'class_of_service',
            'target_price',
        ]

    # 自定义字段
    target_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter target price'}))
    flight = forms.ModelChoiceField(queryset=Flight.objects.all(), required=False,
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    seat_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter seat number'}))
    airline_company = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter airline company'}))
    class_of_service = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter class of service'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 将自动匹配字段只读
        self.fields['origin'].widget.attrs['readonly'] = True
        self.fields['destination'].widget.attrs['readonly'] = True
        self.fields['departure_date'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True
        self.fields['current_price'].widget.attrs['readonly'] = True  # 当前价位只读

    # 自定义表单字段的验证
    def clean_target_price(self):
        target_price = self.cleaned_data.get('target_price')
        if target_price is None:
            raise forms.ValidationError("Target price is required.")
        if target_price is not None and target_price < 0:
            raise forms.ValidationError("Target price cannot be negative.")
        return target_price

    # 根据航班号匹配
    def clean_flight_number(self):
        fn = self.cleaned_data['flight_number'].strip()
        try:
            flight = Flight.objects.get(flight_number=fn)
        except Flight.DoesNotExist:
            raise forms.ValidationError("No matching flight found for this flight number.")

        # 自动匹配信息
        self.instance.origin = flight.origin
        self.instance.destination = flight.destination
        self.instance.departure_date = flight.departure_date
        self.instance.status = flight.status

        return fn
