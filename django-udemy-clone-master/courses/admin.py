from django.contrib import admin

from .models import Category, Course, Lesson, ProctoredExam, ExamAttempt, ViolationRecord, Certificate, ExamQuestion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'level', 'is_published')
    list_filter = ('category', 'level', 'is_published')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')


@admin.register(ProctoredExam)
class ProctoredExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration_minutes', 'passing_score')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_text', 'correct_answer')
    list_filter = ('exam',)
    search_fields = ('question_text', 'exam__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'start_time', 'end_time', 'score', 'status')
    list_filter = ('status', 'exam', 'user')
    search_fields = ('user__email', 'exam__title')
    readonly_fields = ('start_time', 'end_time')


@admin.register(ViolationRecord)
class ViolationRecordAdmin(admin.ModelAdmin):
    list_display = ('exam_attempt', 'violation_type', 'timestamp')
    list_filter = ('violation_type', 'timestamp')
    search_fields = ('exam_attempt__user__email', 'violation_type')
    readonly_fields = ('timestamp',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'issue_date', 'certificate_number')
    list_filter = ('course', 'issue_date')
    search_fields = ('user__email', 'course__title', 'certificate_number')
    readonly_fields = ('issue_date',)
