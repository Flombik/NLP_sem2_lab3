from django.shortcuts import render
from django.views.generic.edit import FormView

from .forms import FileFieldForm
from .models import Document


def perform_file_upload(file, filename: str) -> str:
    path = 'D:/Projects/NLP_sem2_lab3/results/{}'.format(filename)
    with open(path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return path


def add_file_to_db(filepath: str) -> None:
    with open(filepath, 'rt', encoding='utf-8') as file:
        Document.objects.create(title=filepath.split('/')[-1].split('.')[0], text=file.read())


# Create your views here.
def index(request):
    if request.method == 'POST' and request.FILES is not None:
        print(request.FILES)
        for file in request.FILES['files']:
            print(file.name)
        return render(request, 'index.html')
    return render(request, 'index.html')


class FileFieldView(FormView):
    form_class = FileFieldForm
    template_name = 'upload.html'  # Replace with your template.
    success_url = '/'  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            for f in files:
                add_file_to_db(perform_file_upload(f, f.name))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def chose_files():
    pass


def show_results():
    pass
