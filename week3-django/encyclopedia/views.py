from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import markdown2
import random

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    try:
        html_entry = markdown2.markdown(util.get_entry(entry))
    except:
        return HttpResponse("No page exists for: {}".format(entry))
    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "html_entry": html_entry
    })


def search(request):
    if request.method == "POST":
        entries = util.list_entries()
        q = request.POST['q']
        substrings = []
        if q in entries:
            return HttpResponseRedirect(reverse('wiki:entry', args=(q,)))
        else:
            for entry in entries:
                if q in entry:
                    substrings.append(entry)
            return render(request, "encyclopedia/search_results.html", {
                "q": q,
                "substrings": substrings
            })


def newpage(request):
    if request.method == "POST":
        entries = util.list_entries()
        newpost_title = request.POST['title']
        newpost_body = request.POST['body']
        # check for duplicate post
        for entry in entries:
            if newpost_title.lower() == entry.lower():
                return HttpResponse("Error, an entry for {} already exists!".format(newpost_title))

        # add new entry
        with open('entries/{}.md'.format(newpost_title), 'w') as writer:
            writer.write("# " + newpost_title + '\n')
            writer.write('\n')
            writer.write(newpost_body)

        return HttpResponseRedirect(reverse('wiki:entry', args=(newpost_title,)))
    else:
        return render(request, "encyclopedia/newpage.html")


def editpage(request, entry):
    # open and read file
    with open('entries/{}.md'.format(entry), 'r') as reader:
        md_entry = reader.read()

    if request.method == "POST":
        newpost_body = request.POST['body']
        # add new entry
        with open('entries/{}.md'.format(entry), 'w') as writer:
            writer.write(newpost_body)

        return HttpResponseRedirect(reverse('wiki:entry', args=(entry,)))
    else:
        return render(request, "encyclopedia/editpage.html", {
            "entry": entry,
            "md_entry": md_entry
        })


def randompage(request):
    entries = util.list_entries()
    random_entry = entries[random.randint(0, len(entries)-1)]
    return HttpResponseRedirect(reverse('wiki:entry', args=(random_entry,)))