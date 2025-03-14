"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginView

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('academics/', include('academics.urls')),
    path('cafeteria/', include('cafeteria.urls')),
    path('transportation/', include('transportation.urls')),
    path('events/', include('events.urls')),
    path('notifications/', include('notifications.urls')),
    path('navigation/', include('navigation.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('chat/', include('chat.urls')),
    path('security/', include('security.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)