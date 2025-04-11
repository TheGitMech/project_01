from django.core.management.base import BaseCommand
from courses.models import ProctoredExam, ExamQuestion

class Command(BaseCommand):
    help = 'Adds sample questions to the specified exam'

    def add_arguments(self, parser):
        parser.add_argument('exam_id', type=int, help='ID of the exam to add questions to')

    def handle(self, *args, **options):
        exam_id = options['exam_id']
        
        try:
            exam = ProctoredExam.objects.get(id=exam_id)
        except ProctoredExam.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Exam with ID {exam_id} does not exist'))
            return

        # Sample questions for programming exam
        questions = [
            {
                'question': 'What is a variable in programming?',
                'option_a': 'A storage location with a name',
                'option_b': 'A mathematical equation',
                'option_c': 'A type of loop',
                'option_d': 'A function name',
                'correct_answer': 'A storage location with a name'
            },
            {
                'question': 'Which of these is a loop structure?',
                'option_a': 'if-else',
                'option_b': 'for',
                'option_c': 'switch',
                'option_d': 'try-catch',
                'correct_answer': 'for'
            },
            {
                'question': 'What does IDE stand for?',
                'option_a': 'Integrated Development Environment',
                'option_b': 'Internal Development Engine',
                'option_c': 'Interface Design Element',
                'option_d': 'Interactive Data Exchange',
                'correct_answer': 'Integrated Development Environment'
            },
            {
                'question': 'What is the purpose of a function?',
                'option_a': 'To store data',
                'option_b': 'To reuse code',
                'option_c': 'To create variables',
                'option_d': 'To format text',
                'correct_answer': 'To reuse code'
            },
            {
                'question': 'What is an array?',
                'option_a': 'A single value',
                'option_b': 'A collection of values',
                'option_c': 'A type of function',
                'option_d': 'A programming language',
                'correct_answer': 'A collection of values'
            }
        ]

        created_count = 0
        for q in questions:
            ExamQuestion.objects.create(
                exam=exam,
                question_text=q['question'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer']
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} questions to exam "{exam.title}"')
        ) 