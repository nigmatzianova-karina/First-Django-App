from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


from .forms import UserBioForm, UploadFileForm

def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "result": result,
        "a": a,
        "b": b,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)

def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, "requestdataapp/user-view-form.html", context=context)

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # myfile = request.FILES["myfile"]
            myfile = form.cleaned_data['file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print(f"Saved file {filename}")
    else:
        form = UploadFileForm()

    context = {
        "form": form,
    }
    return render(request, "requestdataapp/file-upload.html", context=context)

