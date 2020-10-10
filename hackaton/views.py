# Create your views here.
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import PymeDocumentForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

def hackaton(request):
    return render(request,'hackaton/hackaton.html',{'key':'value'})


def uploadDocument(request):
    if request.method == 'POST':
        form = PymeDocumentForm(request.POST,request.FILES) #Files porque quiero subir un archivo pe papi
        if form.is_valid():
            form.save()
            pyme_name = form.cleaned_data.get('pyme_name')
            print(str(pyme_name))
            messages.success(request, f'The document of the Pyme: {pyme_name} is being processed!')
    else:
        print("form is not valid")
        form = PymeDocumentForm()
    return render(request, 'hackaton/hackaton.html', {'form': form})

