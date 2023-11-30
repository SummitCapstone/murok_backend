# Generated by Django 4.2.7 on 2023-11-30 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('diagnosis', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDiagnosisResult',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('crop_category', models.CharField(choices=[('UNKNOWN', 'Unknown'), ('STRAWBERRY', 'Strawberry'), ('TOMATO', 'Tomato'), ('PEPPER', 'Pepper'), ('CUCUMBER', 'Cucumber')], max_length=50)),
                ('crop_status', models.CharField(blank=True, choices=[('UNKNOWN', '알 수 없음'), ('HEALTHY', '정상'), ('ERROR', '오류'), ('GRAY_MOLD', '잿빛곰팡이병'), ('POWDERY_MILDEW', '흰가루병'), ('DOWNY_MILDEW', '노균병'), ('ANTHRACNOSE', '탄저병'), ('MACRONUTRIENT_DEFICIENCY_NITROGEN', '다량원소결핍(N)'), ('MACRONUTRIENT_DEFICIENCY_PHOSPHORUS', '다량원소결핍(P)'), ('MACRONUTRIENT_DEFICIENCY_POTASSIUM', '다량원소결핍(K)'), ('DEHISCENCE', '열과'), ('COLD_INJURY', '냉해피해'), ('CALCIUM_DEFICIENCY', '칼슘결핍')], max_length=50)),
                ('probability_ranking', models.JSONField()),
                ('request_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='diagnosis.userdiagnosisrequest')),
                ('request_user_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.requestuser')),
            ],
            options={
                'db_table': 'user_diagnosis_report',
                'managed': True,
            },
        ),
    ]
