import pandas as pd
import csv
from django.urls import path
from django.contrib import admin
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from .models import User , Category ,Result , Question ,  Quiz , Option
from rest_framework.authtoken.models import TokenProxy


admin.site.unregister(TokenProxy)
admin.site.unregister(Group)

from .forms import CsvUploadForm
import csv

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

    def has_add_permission(self, request, obj):
        return False

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    change_list_template = 'admin/category/csv_upload_change_list.html'

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
                required_fields = ['category', 'quiz', 'question', 'option1', 'option2', 'option3', 'option4', 'correct_option']

                for field in required_fields:
                    if field not in df.columns:
                        self.message_user(request, f"Required field '{field}' is not present in the CSV.")
                        return redirect("..")


                for index, row in df.iterrows():
                    category_name = row['category']
                    quiz_title = row['quiz']
                    question_text = row['question']
                    option_texts = [row['option1'], row['option2'], row['option3'], row['option4']]
                    correct_option = row['correct_option']
                    try:
                        category = Category.objects.get(category_name=category_name)
                    except:
                        self.message_user(request, "Category not present.")
                        return redirect("..")
                    try:
                        quiz= Quiz.objects.get(category=category, quiz_title=quiz_title)
                    except:
                        self.message_user(request, "Quiz not present.")
                        return redirect("..")
                    question = Question.objects.create(quiz=quiz, question_text=question_text)
                    for i in correct_option.split(","):
                        options = [
                            Option(question=question, option_text=option_text, is_correct_option=option_text == correct_option)
                            for option_text in option_texts
                        ]
                        Option.objects.bulk_create(options)


                self.message_user(request, "Data uploaded successfully.")
                return redirect("..")
        else:
            form = CsvUploadForm()
        return render(request, 'admin/category/csv_upload_form.html', {'form': form})

    csv_upload_view.short_description = "Upload CSV data"

admin.site.register(Category)
admin.site.register(Quiz)
admin.site.register(Question,QuestionAdmin)