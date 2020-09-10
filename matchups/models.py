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

class Meleeframedata(models.Model):
    character = models.TextField(db_column='Character', blank=True, null=True)  # Field name made lowercase.
    move = models.TextField(db_column='Move', blank=True, null=True)  # Field name made lowercase.
    active_hits = models.TextField(db_column='Active_Hits', blank=True, null=True)  # Field name made lowercase.
    total_frames = models.IntegerField(db_column='Total_Frames', blank=True, null=True)  # Field name made lowercase.
    iasa = models.IntegerField(db_column='IASA', blank=True, null=True)  # Field name made lowercase.
    landing_lag = models.IntegerField(db_column='Landing_Lag', blank=True, null=True)  # Field name made lowercase.
    l_cancelled = models.IntegerField(db_column='L_Cancelled', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.
    base_damage = models.TextField(db_column='Base_Damage', blank=True, null=True)  # Field name made lowercase.
    sheild_stun = models.TextField(db_column='Sheild_Stun', blank=True, null=True)  # Field name made lowercase.
    frame_advantage = models.TextField(db_column='Frame_Advantage', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MeleeFrameData'
    
    def __str__(self):
        """
        String representation of a Meleeframedata object.
        """
        return self.character + ': ' + self.move


class Meleeoos(models.Model):
    character = models.TextField(db_column='Character', blank=True, null=True)  # Field name made lowercase.
    move = models.TextField(db_column='Move', blank=True, null=True)  # Field name made lowercase.
    frame = models.TextField(db_column='Frame', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MeleeOOS'

    def __str__(self):
        """
        String representation of a Meleeoos object.
        """
        return self.character + ': ' + self.move