from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from store.models import Product
from tags.models import TaggedItem

# Create your views here.

def say_hello(request):
    content_type=ContentType.objects.get_for_model(Product)
    tagged_items=TaggedItem.objects.select_related('tag').filter(
        content_type=content_type,object__id=1)


    return render(request, 'hello.html',{'name':'mosh','products':list(query_set)})
    