from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import Event, EventRSVP, Club, ClubMembership
from .forms import EventForm, EventRSVPForm

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        queryset = Event.objects.filter(
            end_datetime__gte=timezone.now()
        ).order_by('start_datetime')

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        # Filter by club
        club_id = self.request.GET.get('club')
        if club_id:
            queryset = queryset.filter(organizer_id=club_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = Club.objects.all()
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_rsvp'] = EventRSVP.objects.filter(
                event=self.object,
                user=self.request.user
            ).first()
            context['is_organizer'] = self.object.organizer.memberships.filter(
                user=self.request.user,
                role__in=['president', 'officer']
            ).exists()
        context['rsvp_form'] = EventRSVPForm()
        return context


class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')

    def test_func(self):
        # Check if user is an officer or president of any club
        return ClubMembership.objects.filter(
            user=self.request.user,
            role__in=['president', 'officer']
        ).exists()

    def form_valid(self, form):
        form.instance.organizer = get_object_or_404(
            Club,
            memberships__user=self.request.user,
            memberships__role__in=['president', 'officer']
        )
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def test_func(self):
        event = self.get_object()
        return event.organizer.memberships.filter(
            user=self.request.user,
            role__in=['president', 'officer']
        ).exists()

    def get_success_url(self):
        return reverse_lazy('events:event_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('events:event_list')
    template_name = 'events/event_confirm_delete.html'

    def test_func(self):
        event = self.get_object()
        return event.organizer.memberships.filter(
            user=self.request.user,
            role__in=['president', 'officer']
        ).exists()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)


def rsvp_event(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to RSVP for events.')
        return redirect('login')

    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = EventRSVPForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']

            # Update or create RSVP
            rsvp, created = EventRSVP.objects.update_or_create(
                event=event,
                user=request.user,
                defaults={'status': status}
            )

            messages.success(request, f'Your RSVP status has been updated to {status}.')
        else:
            messages.error(request, 'Invalid RSVP submission.')

    return redirect('events:event_detail', pk=pk)


class MyEventsView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/my_events.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        return Event.objects.filter(
            rsvps__user=self.request.user,
            rsvps__status='going',
            end_datetime__gte=timezone.now()
        ).order_by('start_datetime')

class ClubListView(ListView):
    model = Club
    template_name = 'events/club_list.html'
    context_object_name = 'clubs'
    paginate_by = 12

    def get_queryset(self):
        queryset = Club.objects.all()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset


class ClubDetailView(DetailView):
    model = Club
    template_name = 'events/club_detail.html'
    context_object_name = 'club'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = self.object.events.filter(
            end_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:5]
        context['club_members'] = self.object.memberships.select_related('user')
        if self.request.user.is_authenticated:
            context['user_membership'] = self.object.memberships.filter(
                user=self.request.user
            ).first()
        return context
# Create your views here.
