import os
import pandas as pd
import csv
from django.urls import path
from django.contrib import admin
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from .models import User, Category, Result, Question, Quiz, Option
from rest_framework.authtoken.models import TokenProxy

admin.site.unregister(TokenProxy)
admin.site.unregister(Group)

from .forms import UploadForm
import csv

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['category_name']


class QuizAdmin(admin.ModelAdmin):
    list_filter = ['category__category_name']
    search_fields = ['quiz_title']

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

    def has_add_permission(self, request, obj):
        return False

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    search_fields = ['question_text']
    list_filter = ['quiz__category__category_name' , 'quiz__quiz_title']
    change_list_template = 'admin/category/upload_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-file/', self.upload_file_view, name='upload-file'),
        ]
        return custom_urls + urls

    def upload_file_view(self, request):
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['file']
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                allowed_extensions = ['.csv', '.xls', '.xlsx']

                if file_extension not in allowed_extensions:
                    self.message_user(request, "Invalid file type. Please upload a valid CSV or Excel file.")
                    return redirect("..")

                if file_extension == '.csv':
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                if df.empty:
                    self.message_user(request, "Error reading the file.")
                    return redirect("..")

                required_fields = ['category', 'quiz', 'questions', 'option1', 'option2', 'option3', 'option4', 'correct_option']
 
                missing_fields = [field for field in required_fields if field not in df.columns]
                if missing_fields:
                    self.message_user(request, f"Missing fields: {', '.join(missing_fields)}")
                    return redirect("..")

                for index, row in df.iterrows():
                    category_name = row['category']
                    quiz_title = row['quiz']
                    question_text = row['questions']
                    option_texts = [row['option1'], row['option2'], row['option3'], row['option4']]
                    if 'option5' in df.columns and row['option5']:
                        option_texts.append(row['option5'])
                    option_texts = [opt for opt in option_texts if not pd.isna(opt)]
                    print(row['correct_option'])
                    correct_option_labels = [label.strip() for label in row['correct_option'].split(",")]

                    try:
                        category = Category.objects.get(category_name=category_name)
                    except Category.DoesNotExist:
                        self.message_user(request, "Category not present.")
                        return redirect("..")

                    try:
                        quiz = Quiz.objects.get(category=category, quiz_title=quiz_title)
                    except Quiz.DoesNotExist:
                        self.message_user(request, "Quiz not present.")
                        return redirect("..")

                    question = Question.objects.create(quiz=quiz, question_text=question_text)

                    options = [
                        Option(
                            question=question,
                            option_text=option_text,
                            is_correct_option=(option_text in correct_option_labels)
                        )
                        for option_text in option_texts
                    ]

                    Option.objects.bulk_create(options)

                self.message_user(request, "File uploaded successfully.")
                return redirect("..")
            else:
                self.message_user(request, "Invalid form data.")
                return redirect("..")
        else:
            form = UploadForm()
        return render(request, 'admin/category/upload_form.html', {'form': form})

    upload_file_view.short_description = "Upload or Excel data"

admin.site.register(Category, CategoryAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
