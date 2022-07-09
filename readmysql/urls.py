from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load-more', views.load_more, name='load-more'),
    path('display_vocab', views.display_vocab, name='display_vocab'),
    path('similar/<int:id>', views.similar, name='similar'),
    path('topic_view', views.topic_view, name='topic_view'),
    
]
