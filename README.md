# djeneralize

Generalizations of specialized models for Django.

**djeneralize is not longer under development!**

## Migrating from djeneralize

We have had success migrating djeneralize models to 
[django-polymorphic](https://pypi.python.org/pypi/django_polymorphic). The 
following procedure has worked for us:

1. replace `BaseGeneralizationModel` with `PolymorphicModel`
2. remove all `Meta.specialization_type` attributes
3. replace all `Model.specializations` calls with `Model.objects` calls
4. remove all `as_specialization()` calls
5. run `makemigrations` 
6. manually add migration calling `reset_polymorphic_ctypes` on all Polymorphic 
models
7. run `migrate`


### Example Model Changes and Migrations

For the following djeneralize example model:

```python
from django.db.models.fields import CharField, DateTimeField, ForeignKey, \ 
    TextField, DecimalField
 
from djeneralize.models import BaseGeneralizationModel
 
 
class Question(BaseGeneralizationModel):
    wording = CharField(max_length=256)
    
    
class TextQuestion(Question):
    class Meta:
        specialization = 'text'
        
        
class NumericQuestion(Question):
    unit = CharField(max_length=2)
    
    class Meta:
        specialization = 'numeric'
        
        
class Answer(BaseGeneralizationModel):
    timestamp = DateTimeField(null=True)    
    
    
class TextAnswer(Answer):
    question = ForeignKey(TextQuestion, related_name='answers')
 
    value = TextField()
    
    class Meta:
        specialization = 'text'
 
 
class NumericAnswer(Answer):
    question = ForeignKey(NumericQuestion, related_name='answers')
 
    value = DecimalField()
 
    class Meta:
        specialization = 'numeric'
```

modify it to become:

```python
from django.db.models.fields import CharField, DateTimeField, ForeignKey, \ 
    TextField, DecimalField
 
from polymorphic.models import PolymorphicModel
 
 
class Question(PolymorphicModel):
 
    wording = CharField(max_length=256)
    
    
class TextQuestion(Question):
    pass
        
        
class NumericQuestion(Question):
    unit = CharField(max_length=2)
        
        
class Answer(PolymorphicModel):
    timestamp = DateTimeField(null=True)    
 
 
class TextAnswer(Answer):
    question = ForeignKey(TextQuestion, related_name='answers')
 
    value = TextField()
 
 
class NumericAnswer(Answer):
    question = ForeignKey(NumericQuestion, related_name='answers')
 
    value = DecimalField()
```

Now run `manage.py makemigrations`; imagining that this creates the file `myapp/migrations/0002_auto_20170928_1100.py` 
you must now make the following file (`myapp/migrations/0003_this_name_does_not_matter.py`):

```python
from __future__ import unicode_literals
 
from django.db import migrations
from polymorphic.utils import reset_polymorphic_ctype
 
 
def _update_content_types(apps, schema_editor):
    answer_model = apps.get_model('myapp', 'Answer')
    numeric_answer_model = apps.get_model('myapp', 'NumericAnswer')
    text_answer_model = apps.get_model('myapp', 'TextAnswer')
    
    question_model = apps.get_model('myapp', 'Question')
    numeric_question_model = apps.get_model('myapp', 'NumericQuestion')
    text_question_model = apps.get_model('myapp', 'TextQuestion')
    
    reset_polymorphic_ctype(
        answer_model,
        text_answer_model,
        numeric_answer_model,
    )
     
    reset_polymorphic_ctype(
        question_model,
        text_question_model,
        numeric_question_model,
    )
 
class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0002_auto_20170928_1100'),
    ]
 
    operations = [
        migrations.RunPython(_update_content_types, migrations.RunPython.noop)
    ]

```

Now run `manage.py migrate` and your models should be consistent.

You will have to look through your code to find uses of `djeneralize` specifics, 
but we have had no issues in swapping these for `Polymorphic` patterns.