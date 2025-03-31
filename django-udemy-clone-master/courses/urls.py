from django.urls import include, path
from .views import *
from . import views, views_exam

app_name = 'courses'


urlpatterns = [
    path('courses/<slug:slug>', CourseDetailView.as_view(), name='course-details'),
    path('courses/<slug:slug>/category', CoursesByCategoryListView.as_view(), name='course-by-category'),
    # proctoring integrating part 
    path('start-exam/<int:course_id>/', start_exam, name='start_exam'),
    #proctroing integrating part 

    #payment template
    #path('payments/', include('payments.urls')),

    # Exam URLs
    path('course/<slug:course_slug>/exams/', views_exam.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/start/', views_exam.start_exam, name='start_exam'),
    path('exam/attempt/<int:attempt_id>/', views_exam.exam_in_progress, name='exam_in_progress'),
    path('exam/attempt/<int:attempt_id>/complete/', views_exam.complete_exam, name='complete_exam'),
    path('exam/attempt/<int:attempt_id>/result/', views_exam.exam_result, name='exam_result'),
    path('certificate/<int:certificate_id>/', views_exam.view_certificate, name='view_certificate'),
]
