# Create your views here.
from django.contrib import messages
import pandas as pd
import json
from django.http import HttpResponse,FileResponse,JsonResponse
from .models import Pyme
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

from django.db.models import Model

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

def download(request):

    pymes =Pyme.objects.all()

    temp0=[[i.pyme_name,str(i.pyme_document),str(i.register_created_at),str(i.date),i.mnt_units,i.cashResources,i.totalAssets,i.totalLiabilities,i.totalEquity,i.sales,i.costSales,i.grossProfit,i.operatingProfit,i.profitBeforeTax,i.netProfit,i.accuracy,i.more_info] for i in pymes]
    
    mycolumns=["pyme_name","pyme_document","register_created_at","date","mnt_units","cashResources ","totalAssets ","totalLiabilities ","totalEquity","sales ","costSales ","grossProfit ","operatingProfit","profitBeforeTax ","netProfit","accuracy","more_info"]    
    
    df = pd.DataFrame(temp0,columns=mycolumns)
    
    temp1 = json.dumps(df.to_json(orient="records"),indent=4)

    response = FileResponse(temp1)

    #messages.success(request, f'Archivo descargado')

    return response

def retrieveInformation(request):
    #obj = Pyme.objects.get(id=id)
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

    pymes=list(Pyme.objects.all())

    df = pd.DataFrame(pymes)

    messages.success(request, f'Information is being retrieved')

    return render(request,'hackaton/hackaton.html',{'pymes_key':pymes,'form':form})

