from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView, ListView,DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Review
from .forms import ReviewForm

# Create your views here.
def home(request):
    return render(request, "index.html",)

class About(CreateView, ListView):
    model = Review
    form_class = ReviewForm
    template_name = 'about.html'
    context_object_name = 'reviews'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return Review.objects.all()


class Portfolio(ListView):
    model = Review
    template_name = 'portfolio.html'
    context_object_name = 'reviews'

def services(request):
    return render(request, "services.html",)

def design(request):
    return render(request, "design.html",)

def development(request):
    return render(request, "development.html",)

def seo(request):
    return render(request, "seo.html",)

def maintenance(request):
    return render(request, "maintenance.html",)


class ReviewDeleteView(DeleteView):
    model = Review
    template_name = 'review_confirm_delete.html'
    success_url = reverse_lazy('home')

