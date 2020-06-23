# Generated by Django 3.0.7 on 2020-06-23 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Framedata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character', models.TextField(blank=True, db_column='Character', null=True)),
                ('move', models.TextField(blank=True, db_column='Move', null=True)),
                ('startup', models.TextField(blank=True, db_column='Startup', null=True)),
                ('totalframes', models.TextField(blank=True, db_column='TotalFrames', null=True)),
                ('landinglag', models.TextField(blank=True, db_column='LandingLag', null=True)),
                ('additionalnotes', models.TextField(blank=True, db_column='AdditionalNotes', null=True)),
                ('basedamage', models.TextField(blank=True, db_column='BaseDamage', null=True)),
                ('shieldlag', models.TextField(blank=True, db_column='Shieldlag', null=True)),
                ('shieldstun', models.TextField(blank=True, db_column='Shieldstun', null=True)),
                ('hitbox', models.TextField(blank=True, db_column='Hitbox', null=True)),
                ('advantage', models.TextField(blank=True, db_column='Advantage', null=True)),
            ],
            options={
                'db_table': 'framedata',
                'managed': False,
            },
        ),
    ]
