from django import forms
from .models import Auction, Bid, Comment, Category

DURATION_CHOICES = [
    (1, "1 day"),
    (2, "2 days"),
    (3, "3 days"),
    (4, "4 days"),
    (5, "5 days"),
    (6, "6 days"),
    (7, "7 days"),
]

class AuctionForm(forms.ModelForm):
    title = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
    starting_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, required=True)
    image = forms.ImageField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=True, label="Auction Duration")


    class Meta:
        model = Auction
        fields = ['title', 'description', 'starting_price', 'image', 'category']
