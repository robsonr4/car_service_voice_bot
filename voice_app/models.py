from django.db import models

# Create your models here.

class Car(models.Model):
    marka_options = (
        ('lexus', 'lexus'),
        ('toyota', 'toyota'),
    )

    marka = models.CharField(max_length=6, choices=marka_options)

    model = models.CharField(max_length=20)

    rok_produkcji = models.IntegerField()

    def __str__(self):
        return self.marka + " " + self.model + " " + str(self.rok_produkcji)
