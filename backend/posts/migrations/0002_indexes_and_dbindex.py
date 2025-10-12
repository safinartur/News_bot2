from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(blank=True, max_length=80, unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, unique=True, db_index=True),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-created_at'], name='posts_post_created_idx'),
        ),
    ]
