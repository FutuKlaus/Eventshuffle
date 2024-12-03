from django.http import JsonResponse
from eventshuffle.models import Event, EventDate
from eventshuffle.models import Event
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def event_list(request):
    events = Event.objects.values('id', 'name')
    return JsonResponse({'events': list(events)})

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
            EventDate(event=event, date=date, people=[]) for date in event_dates
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

    return JsonResponse(response_data)


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


        person_name = request.data.get('name')
        chosen_dates = request.data.get('votes', [])

        if not person_name or len(chosen_dates) == 0:
            return JsonResponse({'error': 'Names and votes are required fields'})

        event = Event.objects.get(id=id)
        event_dates = EventDate.objects.filter(event=event, date__in=chosen_dates)
        if not event_dates.exists():
            return JsonResponse({'error': 'No such dates found in the event'})


        for date in event_dates:
            if person_name not in date.people:
                date.people.append(person_name)
                date.save()

        response = generate_event_json(event, event_dates)

        return response
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_results(request, id):
    try:
        event = Event.objects.get(id=id)
        event_dates = EventDate.objects.filter(event=event)

        people_amount = len(set(
            person for date in event_dates for person in date.people
        ))

        suitable_dates = []

        for date in event_dates:
            if len(date.people) == people_amount:
                suitable_dates.append({
                    'date': date.date,
                    'people': date.people
                })

        response_data =  {
            'id': event.id,
            'name': event.name,
            'suitableDates': suitable_dates,
        }

        return JsonResponse(response_data)

    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


