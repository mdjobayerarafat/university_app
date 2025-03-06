from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q


from .models import Cafeteria, MenuItem, DailyMenu, Order, OrderItem
from .forms import OrderForm, OrderItemForm



class CafeteriaListView(ListView):
    model = Cafeteria
    template_name = 'cafeteria/cafeteria_list.html'
    context_object_name = 'cafeterias'


class CafeteriaDetailView(DetailView):
    model = Cafeteria
    template_name = 'cafeteria/cafeteria_detail.html'
    context_object_name = 'cafeteria'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context['daily_menu'] = DailyMenu.objects.filter(cafeteria=self.object, date=today).first()
        return context


class MenuItemListView(ListView):
    model = MenuItem
    template_name = 'cafeteria/menu_items.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')

        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return queryset


class DailyMenuView(View):
    def get(self, request):
        date = request.GET.get('date', timezone.now().date())
        cafeteria_id = request.GET.get('cafeteria')

        if cafeteria_id:
            cafeteria = get_object_or_404(Cafeteria, id=cafeteria_id)
            daily_menu = DailyMenu.objects.filter(cafeteria=cafeteria, date=date).first()
            if daily_menu:
                return render(request, 'cafeteria/daily_menu.html', {'daily_menu': daily_menu})
            else:
                messages.info(request, "No menu available for this date.")
                return render(request, 'cafeteria/daily_menu.html')
        else:
            cafeterias = Cafeteria.objects.all()
            return render(request, 'cafeteria/select_cafeteria.html', {'cafeterias': cafeterias})


class CreateOrderView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'cafeteria/create_order.html'
    success_url = reverse_lazy('cafeteria:my_orders')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cafeteria_id = self.request.GET.get('cafeteria')
        if cafeteria_id:
            cafeteria = get_object_or_404(Cafeteria, id=cafeteria_id)
            today = timezone.now().date()
            daily_menu = DailyMenu.objects.filter(
                cafeteria=cafeteria,
                date=today
            ).first()
            if daily_menu:
                context['menu_items'] = daily_menu.items.all()
            context['cafeteria'] = cafeteria
        return context

    def form_valid(self, form):
        try:
            if not form.is_valid():
                print("Form errors:", form.errors)
                return self.form_invalid(form)

            # Save the order instance
            order = form.save(commit=False)
            order.user = self.request.user
            order.total_price = 0  # Initialize total price
            order.save()

            # Process order items
            total_price = 0
            for item_id, quantity in self.request.POST.items():
                if item_id.startswith('quantity-') and int(quantity) > 0:
                    item_id = item_id.replace('quantity-', '')
                    menu_item = MenuItem.objects.get(id=item_id)
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        price=menu_item.price
                    )
                    total_price += menu_item.price * int(quantity)

            # Update the order's total price
            order.total_price = total_price
            order.save()

            return super().form_valid(form)
        except Exception as e:
            print("Error:", str(e))  # Debugging: Print error
            return self.form_invalid(form)


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'cafeteria/my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'cafeteria/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


