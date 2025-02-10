from django.shortcuts import render
from django.http import HttpResponse
def index(request):
    return HttpResponse("Rango says hey there partner! <br><a href='/rango/about/'>About Page</a>")

def about(request):
    return HttpResponse("Rango says here is the about page. <br><a href='/rango/'>Back to Index</a>")



# Create your views here.
