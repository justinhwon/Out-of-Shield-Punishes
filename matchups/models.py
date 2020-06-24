from django.db import models

# Create your models here.
class Framedata(models.Model):
    character = models.TextField(db_column='Character', blank=True, null=True)  # Field name made lowercase.
    move = models.TextField(db_column='Move', blank=True, null=True)  # Field name made lowercase.
    startup = models.TextField(db_column='Startup', blank=True, null=True)  # Field name made lowercase.
    totalframes = models.TextField(db_column='TotalFrames', blank=True, null=True)  # Field name made lowercase.
    landinglag = models.TextField(db_column='LandingLag', blank=True, null=True)  # Field name made lowercase.
    additionalnotes = models.TextField(db_column='AdditionalNotes', blank=True, null=True)  # Field name made lowercase.
    basedamage = models.TextField(db_column='BaseDamage', blank=True, null=True)  # Field name made lowercase.
    shieldlag = models.TextField(db_column='Shieldlag', blank=True, null=True)  # Field name made lowercase.
    shieldstun = models.TextField(db_column='Shieldstun', blank=True, null=True)  # Field name made lowercase.
    hitbox = models.TextField(db_column='Hitbox', blank=True, null=True)  # Field name made lowercase.
    advantage = models.TextField(db_column='Advantage', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'framedata'

    def __str__(self):
        """
        String representation of a Framedata object.
        """
        return self.character + ': ' + self.move