# Generated by Django 2.2.16 on 2022-12-09 04:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_comments'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created'], 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.RenameField(
            model_name='post',
            old_name='pub_date',
            new_name='created',
        ),
    ]
