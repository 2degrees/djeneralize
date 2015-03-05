from django.db import models

from djeneralize.manager import SpecializationManager
from djeneralize.models import BaseGeneralizationModel

__all__ = [
    'FruitManager', 'SpecializedFruitManager', 'Fruit', 'Apple', 'Banana'
    ]

class FruitManager(models.Manager):
    """By default we don't want to return any rotten fruit"""
    
    def get_queryset(self):
        return super(FruitManager, self).get_queryset().filter(rotten=False)
    
class SpecializedFruitManager(SpecializationManager):
    """
    And any specializations also shouldn't return any rotten fruit
    specializations.
    
    """
    
    def get_queryset(self):
        return super(SpecializedFruitManager, self).get_queryset().filter(
            rotten=False
            )


class Fruit(BaseGeneralizationModel):
    """A piece of fruit"""
    
    name = models.CharField(max_length=30)
    rotten = models.BooleanField(default=False)
    
    objects = FruitManager()
    specializations = SpecializedFruitManager()
    
    def __unicode__(self):
        return self.name
    
    
class Apple(Fruit):
    """An apple"""
    
    radius = models.IntegerField()
    
    class Meta:
        specialization = 'apple'

        
class Banana(Fruit):
    """A banana"""
    
    curvature = models.DecimalField(max_digits=3, decimal_places=2)
    
    class Meta:
        specialization = 'banana'