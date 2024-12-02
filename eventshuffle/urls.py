from django.urls import path

from eventshuffle.views import event_list, create_event, get_specific_event, add_vote

urlpatterns = [
    
    path('<int:id>/', get_specific_event, name='event-show'),
    path('', create_event, name='event-create'),
    path('list/', event_list, name='event-list'),
    path('<int:id>/vote/', add_vote, name='add_vote'),
    
]