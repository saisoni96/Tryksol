import pandas as pd
import csv
from django.urls import path
from django.contrib import admin
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from .models import User , Category ,Result , Questions

admin.site.unregister(Group)

from .forms import CsvUploadForm
import csv

class CsvDataAdmin(admin.ModelAdmin):
    change_list_template = 'admin/csv_upload_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.csv_upload_view, name='upload-csv'),
        ]
        return custom_urls + urls

    def csv_upload_view(self, request):
        if request.method == 'POST':
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                df = pd.read_csv(csv_file)
                column_headers = df.columns.tolist()
                required_columns = ['category','question','option1','option2','option3','option4','correct_option']

                if required_columns != column_headers:
                    print("7777777777")
                    pass
                else:
                    for index, row in df.iterrows():
                        print("1111111111")
                        category, _ = Category.objects.get_or_create(name=row['category'])
                        questions = Questions.objects.create(category=category, title=row['question'], option1=row['option1'], option2=row['option2'], option3=row['option3'], option4=row['option4'], correct_option=row['correct_option'])
                self.message_user(request, "Data uploaded successfully.")
                return redirect("..")
        else:
            form = CsvUploadForm()
        return render(request, 'admin/csv_upload_form.html', {'form': form})

    csv_upload_view.short_description = "Upload CSV data"

admin.site.register(Category, CsvDataAdmin)
admin.site.register(Questions)
