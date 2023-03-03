# Create your models here.
from django.db import models

GRAPH_CHOICES = [('CMassX', 'CMassX'), ('CMassY', 'CMassY'), ('CMassZ', 'CMassZ'), ('FWHMX', 'FWHMX'),
                 ('FWHMY', 'FWHMY'), ('FWHMZ', 'FWHMZ'), ('Ghost', 'Ghost'), ('BrightGhost', 'BrightGhost')]
class DateChoice(models.Model):
    scandate = models.DateField()

    def __str__(self):
        return self.scandate

class Scanner(models.Model):
    scandate = models.ForeignKey(DateChoice, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Coil(models.Model):
    name = models.CharField(max_length=100)
    scanner = models.ForeignKey(Scanner, on_delete=models.SET_NULL, null=True)
    scandate = models.ForeignKey(DateChoice, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Graph(models.Model):
    graph = models.CharField(max_length=12, choices=GRAPH_CHOICES, default='green')
