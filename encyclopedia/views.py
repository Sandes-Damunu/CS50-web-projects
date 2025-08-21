from django.shortcuts import render, redirect

from . import util
import random
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request ,title):
    content = util.get_entry(title)

    if content is None:
        return render (request , "encyclopedia/error.html", {
            "title": title
        })
    else:
        return render (request , "encyclopedia/entry.html", {
            "title": title , 
            "content": html_content
        })

def search (request):
    query =  request.GET.get('q')
    all_entries= util.list_entries()

    for entry in all_entries:
        if query.lower() == entry.lower():
            return redirect('entry', title=entry)

    partial_matches = []
    for entry in all_entries:
        if query.lower() in entry.lower():
            partial_matches.append(entry)

    return render(request, 'encyclopedia/search_results.html', {
        'query':query,
        'results':partial_matches
    })

def create(request):
    if request.method == "GET":
        return render(request,"encyclopedia/create.html")

    elif request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')

        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/create.html", {
                "error": f'An entry with the tittle "{title}" already exists.'
            })
        util.save_entry(title,content)
        return redirect('entry', title=title)

def edit(request, title):
    
    content= util.get_entry(title)
    if content is None:
        return render (request , "encyclopedia/error.html", {
            "message": f"Page '{title}' not found."
        })
    if request.method =="GET":
        return render(request, "encyclopedia/edit.html", {
            "title":title,
            "content":content
        })
    elif request.method =="POST":
        new_content= request.POST.get('content')

        if not new_content or not new_content.strip():
            return render(request, "encyclopedia/edit.html", {
                "title":title,
                "content":content,
                "error":"Content cannot be empty."
            })

        util.save_entry(title,new_content)
        return redirect('entry', title=title)


def random_page(request):
    entries= util.list_entries()
    if not entries:
        return redirect("index")
    random_entry= random.choice(entries)
    return redirect('entry', title=random_entry)

def entry(request, title):
    content = util.get_entry(title)
    if content:
        html_content = markdown2.markdown(content)
        return render(request, 'encyclopedia/entry.html', {
            'title': title,
            'content': html_content
        })