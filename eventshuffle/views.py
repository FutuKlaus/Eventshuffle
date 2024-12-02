from django.http import HttpResponse, JsonResponse
from eventshuffle.models import Event, EventDate, Vote
from rest_framework import serializers
from eventshuffle.models import Event
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name'] 


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate
        fields = ['date']

class VoteSerializer(serializers.Serializer):
    date = serializers.DateField(format='%Y-%m-%d')
    people = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )


class EventCreateSerializer(serializers.ModelSerializer):
    dates = serializers.ListField(
        child=serializers.DateField(format='%Y-%m-%d'),
        write_only=True
    )

    class Meta:
        model = Event
        fields = ['id', 'name', 'dates']

    def create(self, validated_data):
        dates = validated_data.pop('dates', [])
        event = Event.objects.create(**validated_data)
        for date in dates:
            EventDate.objects.create(event=event, date=date)
        return event

class EventShowSerializer(serializers.ModelSerializer):
    dates = serializers.ListField(
        child=serializers.DateField(format='%Y-%m-%d'),
        read_only=True
    )

    votes = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'dates', 'votes']
    
    def get_votes(self, obj):
        # Get all votes grouped by date
        votes = obj['votes']
        return votes
        
    

class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all()  # Fetch all events
        serializer = EventSerializer(events, many=True)
        print(serializer.data)
        return JsonResponse({"events": serializer.data}, status=status.HTTP_200_OK)
    
class EventCreateView(APIView):
    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response({"id": event.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventShowView(APIView):
    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            dates = list(map(lambda entry: entry.date, event.dates.all()))
            print(event.dates.all()[0].votes.all())
            validDates = list(filter(lambda date: len(date.votes.all()) > 0, event.dates.all()))
            votes = []
            for validDate in validDates:
                line = {"date": validDate.date, "people": list(map(lambda entry: entry.person, validDate.votes.all()))}
                votes.append(line)


            data = {"id": event.id, "name": event.name, "dates": dates, "votes": votes}

            serializer = EventShowSerializer(data)
            return JsonResponse(serializer.data)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)

        