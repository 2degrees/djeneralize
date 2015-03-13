from django.db import models

from djeneralize.fields import SpecializedForeignKey
from djeneralize.models import BaseGeneralizationModel


class Shop(models.Model):

    name = models.CharField(max_length=30)
    producer = SpecializedForeignKey('FruitProducer', related_name='shops')


class FruitProducer(BaseGeneralizationModel):

    name = models.CharField(max_length=30)
    pen = models.ForeignKey('writing.WritingImplement')
    produce = SpecializedForeignKey('fruit.Fruit')


class EcoProducer(FruitProducer):

    fertilizer = models.CharField(max_length=30)

    class Meta:
        specialization = 'eco_producer'


class StandardProducer(FruitProducer):

    chemicals = models.CharField(max_length=30)

    class Meta:
        specialization = 'standard_producer'
