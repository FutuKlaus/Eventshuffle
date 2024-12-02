from django.urls import path

from eventshuffle.views import EventListView, EventCreateView, EventShowView

urlpatterns = [
    path('', EventCreateView.as_view(), name='event-create'),
    path('list/', EventListView.as_view(), name='event-list'),
    path('<int:event_id>/',EventShowView.as_view(), name='event-show'),
    
]