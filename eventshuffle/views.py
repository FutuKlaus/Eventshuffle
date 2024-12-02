from django.http import HttpResponse, JsonResponse
from eventshuffle.models import Event, EventDate, Vote
from eventshuffle.models import Event
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def event_list(request):
    events = Event.objects.values('id', 'name')
    return Response({'events': events})

@api_view(['POST'])
def create_event(request):
    try:
        # Extract data from the request
        event_name = request.data.get('name')
        event_dates = request.data.get('dates', [])

        # Validate input
        if not event_name or not isinstance(event_dates, list):
            return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Event
        event = Event.objects.create(name=event_name)

        # Create EventDate instances
        event_date_objects = [
            EventDate(event=event, date=date, attendees=[]) for date in event_dates
        ]
        EventDate.objects.bulk_create(event_date_objects)

        # Return response with the ID of the created event
        return Response({'id': event.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

def generate_event_json(event, event_dates):
    response_data =  {
        'id': event.id,
        'name': event.name,
        'dates': [entry.date for entry in event_dates],
        'votes': [
            {
                'date': entry.date,
                'people': entry.people,
            }
            for entry in event_dates if entry.people
        ],
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_specific_event(request, id):
    try:
        event = Event.objects.get(id=id)
        event_dates = EventDate.objects.filter(event=event)

        response = generate_event_json(event, event_dates)

        return response

    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def add_vote(request, id):
    try:
        event = Event.objects.get(id=id)
        event_dates = EventDate.objects.filter(event=event)

        person_name = request.data.get('name')
        chosen_dates = request.data.get('votes', [])

        for date in event_dates:
            if date.date in chosen_dates:
                date.people.append(person_name)
        
        response = generate_event_json(event, event_dates)

        return response
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

