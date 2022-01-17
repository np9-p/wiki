from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import util
from markdown2 import Markdown
from django import forms
import secrets

markdowner = Markdown()

class NewEntryForm(forms.Form):
    title = forms.CharField(label = "Entry Title",
        widget=forms.TextInput(attrs={'class':'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(label="Entry Content",
        widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8','rows': 7,'autofocus':'on'}))

class Edit(forms.Form):
    content = forms.CharField(label="Entry Content",
        widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8','rows': 7,'autofocus':'on'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request,entry):
    result = util.get_entry(entry)
    if result is not None:
        return render(request,"encyclopedia/entry.html",{
            "content": markdowner.convert(result),
            "title": entry
        })
    else:
        return render(request,"encyclopedia/not_found.html",{
            "title": entry
        })

def search(request):
    value = request.GET.get("q","")
    result = util.get_entry(value)
    if result is not None:
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': value}))
    else:
        lists = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                lists.append(entry)
        return render(request,"encyclopedia/index.html",{
            "entries": lists,
            "searching": True,
            "value": value
        })

def create(request):
    if request.method != "POST":
        return render(request, "encyclopedia/create.html",{
            "form": NewEntryForm,
            "exists" : False
        })
    else:
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            check = "False"
            for entry in util.list_entries():
                if title.lower() == entry.lower():
                    check = "True"
            if check:
                content = form.cleaned_data["content"]
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry",kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/create.html",{
                    "exists" : True,
                    "form": NewEntryForm
                })

def edit(request, entry):
    entry_page = util.get_entry(entry)
    if request.method == "GET":
        return render(request,"encyclopedia/edit.html",{
            "edit":Edit(initial={'content':entry_page}),
            "entry":entry
        })
    else:
        form = Edit(request.POST)
        if form.is_valid():
            page = form.cleaned_data["content"]
            util.save_entry(entry,page)
            return HttpResponseRedirect(reverse("entry",kwargs={'entry':entry}))


def random(request):
    entry = util.list_entries()
    random = secrets.choice(entry)
    return HttpResponseRedirect(reverse('entry',kwargs={'entry':random}))