from django.db import models

from djeneralize.models import BaseGeneralizationModel

#{ General model

class WritingImplement(BaseGeneralizationModel):
    name = models.CharField(max_length=30)
    length = models.IntegerField()
    
    def __unicode__(self):
        return self.name

#}

#{ Direct children of WritingImplement, i.e. first specializtion 

class Pencil(WritingImplement):
    
    lead = models.CharField(max_length=2) # i.e. HB, B2, H5
    
    class Meta:
        specialization = 'pencil'
        
class Pen(WritingImplement):
    
    ink_colour = models.CharField(max_length=30)
    
    class Meta:
        specialization = 'pen'

#}
    
#{ Grand-children of WritingImplement, i.e. second degree of specialization

class FountainPen(Pen):
    
    nib_width = models.DecimalField(max_digits=3, decimal_places=2)
    
    class Meta:
        specialization = 'fountain_pen'
        
        
class BallPointPen(Pen):
    
    replaceable_insert = models.BooleanField(default=False)
    
    class Meta:
        specialization = 'ballpoint_pen'
 
#}