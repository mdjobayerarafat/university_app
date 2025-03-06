from django.views.generic import ListView, DetailView
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from .models import Building, Room, ARMarker

class BuildingListView(ListView):
    model = Building
    template_name = 'navigation/building_list.html'
    context_object_name = 'buildings'
    paginate_by = 12

    def get_queryset(self):
        queryset = Building.objects.all()
        search_query = self.request.GET.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset

class BuildingDetailView(DetailView):
    model = Building
    template_name = 'navigation/building_detail.html'
    context_object_name = 'building'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = self.object.rooms.all().order_by('floor', 'number')
        context['markers'] = self.object.markers.all()
        return context

class RoomListView(ListView):
    model = Room
    template_name = 'navigation/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 20

    def get_queryset(self):
        queryset = Room.objects.all().select_related('building')
        building_id = self.request.GET.get('building')
        floor = self.request.GET.get('floor')
        room_type = self.request.GET.get('type')
        search = self.request.GET.get('search')

        if building_id:
            queryset = queryset.filter(building_id=building_id)
        if floor:
            queryset = queryset.filter(floor=floor)
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(building__name__icontains=search)
            )

        return queryset.order_by('building__name', 'floor', 'number')

class RoomDetailView(DetailView):
    model = Room
    template_name = 'navigation/room_detail.html'
    context_object_name = 'room'

class ARMarkerListView(ListView):
    model = ARMarker
    template_name = 'navigation/armarker_list.html'
    context_object_name = 'markers'
    paginate_by = 20

    def get_queryset(self):
        queryset = ARMarker.objects.all().select_related('building')

        # Get user's location from query parameters
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')

        if lat and lng:
            user_location = Point(float(lng), float(lat), srid=4326)
            queryset = queryset.annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')

        return queryset

class ARMarkerDetailView(DetailView):
    model = ARMarker
    template_name = 'navigation/armarker_detail.html'
    context_object_name = 'marker'

class NearbyLocationsView(ListView):
    model = Building
    template_name = 'navigation/nearby_locations.html'
    context_object_name = 'locations'

    def get_queryset(self):
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        radius = self.request.GET.get('radius', 1000)  # Default 1km radius

        if lat and lng:
            user_location = Point(float(lng), float(lat), srid=4326)
            return Building.objects.annotate(
                distance=Distance('location', user_location)
            ).filter(distance__lte=radius).order_by('distance')

        return Building.objects.none()

# Create your views here.
