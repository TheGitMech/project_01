from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_category_id_alter_category_title_and_more'),
        ('accounts', '0003_alter_user_first_name_alter_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProctoredExam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('duration_minutes', models.IntegerField(default=60)),
                ('passing_score', models.IntegerField(default=50)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proctored_exams', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='ExamAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('score', models.IntegerField(null=True)),
                ('trust_score', models.FloatField(null=True)),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CHEATING_DETECTED', 'Cheating Detected')], default='IN_PROGRESS', max_length=20)),
                ('profile_image', models.CharField(max_length=255, null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.proctoredexam')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('violation_type', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField()),
                ('exam_attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='violations', to='courses.examattempt')),
            ],
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('certificate_number', models.CharField(max_length=50, unique=True)),
                ('pdf_file', models.CharField(max_length=255, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
                ('exam_attempt', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.examattempt')),
            ],
        ),
    ] 