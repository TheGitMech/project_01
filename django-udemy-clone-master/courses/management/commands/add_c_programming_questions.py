from django.core.management.base import BaseCommand
from courses.models import ProctoredExam, ExamQuestion

class Command(BaseCommand):
    help = 'Adds C programming specific questions to the specified exam'

    def add_arguments(self, parser):
        parser.add_argument('exam_id', type=int, help='ID of the exam to add questions to')

    def handle(self, *args, **options):
        exam_id = options['exam_id']
        
        try:
            exam = ProctoredExam.objects.get(id=exam_id)
        except ProctoredExam.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Exam with ID {exam_id} does not exist'))
            return

        # C Programming specific questions
        questions = [
            {
                'question': 'What is the correct way to declare a pointer variable in C?',
                'option_a': 'int ptr;',
                'option_b': 'int *ptr;',
                'option_c': 'int &ptr;',
                'option_d': 'pointer int ptr;',
                'correct_answer': 'int *ptr;'
            },
            {
                'question': 'Which of the following is the correct way to open a file in C for reading?',
                'option_a': 'fopen("file.txt", "r");',
                'option_b': 'open("file.txt", "read");',
                'option_c': 'fileopen("file.txt", "r");',
                'option_d': 'readfile("file.txt");',
                'correct_answer': 'fopen("file.txt", "r");'
            },
            {
                'question': 'What is the size of int data type in C?',
                'option_a': 'Depends on the compiler and system',
                'option_b': 'Always 2 bytes',
                'option_c': 'Always 4 bytes',
                'option_d': 'Always 8 bytes',
                'correct_answer': 'Depends on the compiler and system'
            },
            {
                'question': 'Which operator is used for accessing value at address stored in a pointer?',
                'option_a': '&',
                'option_b': '*',
                'option_c': '->',
                'option_d': '.',
                'correct_answer': '*'
            },
            {
                'question': 'What is the purpose of malloc() function in C?',
                'option_a': 'To free memory',
                'option_b': 'To allocate static memory',
                'option_c': 'To allocate dynamic memory',
                'option_d': 'To reallocate memory',
                'correct_answer': 'To allocate dynamic memory'
            },
            {
                'question': 'What is the correct syntax for a for loop in C?',
                'option_a': 'for (initialization; condition; increment/decrement)',
                'option_b': 'for (condition; initialization; increment/decrement)',
                'option_c': 'for (increment/decrement; condition; initialization)',
                'option_d': 'for (initialization; increment/decrement; condition)',
                'correct_answer': 'for (initialization; condition; increment/decrement)'
            },
            {
                'question': 'Which header file is required for printf() function?',
                'option_a': '<stdlib.h>',
                'option_b': '<math.h>',
                'option_c': '<stdio.h>',
                'option_d': '<string.h>',
                'correct_answer': '<stdio.h>'
            },
            {
                'question': 'What is the purpose of break statement in C?',
                'option_a': 'To continue with next iteration',
                'option_b': 'To exit from a loop or switch',
                'option_c': 'To skip the current iteration',
                'option_d': 'To terminate the program',
                'correct_answer': 'To exit from a loop or switch'
            },
            {
                'question': 'What is a structure in C?',
                'option_a': 'A pointer type',
                'option_b': 'A user-defined data type that groups related data',
                'option_c': 'An array type',
                'option_d': 'A built-in data type',
                'correct_answer': 'A user-defined data type that groups related data'
            },
            {
                'question': 'What is the purpose of sizeof operator in C?',
                'option_a': 'To find length of string',
                'option_b': 'To find size of array',
                'option_c': 'To find size of data type or variable in bytes',
                'option_d': 'To find memory address',
                'correct_answer': 'To find size of data type or variable in bytes'
            }
        ]

        # Delete existing questions for this exam
        ExamQuestion.objects.filter(exam=exam).delete()

        # Add new questions
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
            self.style.SUCCESS(f'Successfully added {created_count} C programming questions to exam "{exam.title}"')
        ) 