from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0069_user_linkedin_url'),
    ]

    operations = [
        migrations.DeleteModel(name='WorkExperience'),
        migrations.DeleteModel(name='TeacherProfile'),
    ]
