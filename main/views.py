from django.shortcuts import render

# Create your views here.

def index(request):
    context = {'name': 'Misha'}

    return render(request, template_name='main/index.html', context=context)
