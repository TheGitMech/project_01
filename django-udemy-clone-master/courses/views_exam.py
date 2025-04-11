from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from .models import Course, ProctoredExam, ExamAttempt, Certificate
import uuid
import urllib.parse

@login_required
def exam_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    exams = ProctoredExam.objects.filter(course=course)
    return render(request, 'courses/exam_list.html', {
        'course': course,
        'exams': exams
    })

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(ProctoredExam, id=exam_id)
    
    # Check if there's an ongoing attempt
    ongoing_attempt = ExamAttempt.objects.filter(
        user=request.user,
        exam=exam,
        status='IN_PROGRESS'
    ).first()
    
    if ongoing_attempt:
        return redirect('courses:exam_in_progress', attempt_id=ongoing_attempt.id)
    
    # Create new attempt
    attempt = ExamAttempt.objects.create(
        user=request.user,
        exam=exam,
        status='IN_PROGRESS'
    )
    
    return redirect('courses:exam_in_progress', attempt_id=attempt.id)

@login_required
def exam_in_progress(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, user=request.user)
    
    # Build parameters for Flask app
    params = {
        'attempt_id': attempt_id,
        'user_id': request.user.id,
        'username': request.user.get_full_name() or request.user.email.split('@')[0],
        'email': request.user.email,
        'exam_id': attempt.exam.id,
        'exam_name': attempt.exam.title,
        'course_id': attempt.exam.course.slug
    }
    
    # Encode parameters for URL
    encoded_params = urllib.parse.urlencode(params)
    
    # Get the Flask app URL with debug information
    proctor_url = f"http://localhost:5000/exam?{encoded_params}"
    print(f"Debug - Proctor URL: {proctor_url}")
    
    return render(
        request=request,
        template_name='courses/exam_in_progress.html',
        context={
            'attempt': attempt,
            'proctor_url': proctor_url,
            'debug_params': params
        }
    )

@login_required
def complete_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, user=request.user)
    
    if request.method == 'POST':
        # Update attempt status
        attempt.status = 'COMPLETED'
        attempt.save()
        
        # Generate certificate if passed
        if attempt.score >= attempt.exam.passing_score and attempt.trust_score >= 70:
            certificate = Certificate.objects.create(
                user=request.user,
                course=attempt.exam.course,
                exam_attempt=attempt,
                certificate_number=f"CERT-{uuid.uuid4().hex[:8].upper()}"
            )
            return redirect('courses:view_certificate', certificate_id=certificate.id)
    
    return redirect('courses:exam_result', attempt_id=attempt_id)

@login_required
def exam_result(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, user=request.user)
    return render(request, 'courses/exam_result.html', {
        'attempt': attempt
    })

@login_required
def view_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    return render(request, 'courses/certificate.html', {
        'certificate': certificate
    }) 