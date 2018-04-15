"""vertigodjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from vertigo import views
from vertigo.models import Equipment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<slug:url_type>/accord/', views.agreement_page, name='agreement_url'),

    path('<slug:url_type>/', views.list_page, name='list_url'),
    path('<slug:url_type>/emprunt/id-<int:equipment_id>', views.borrowing_page, name='borrowing_url'),

    path('', views.list_page, {'url_type': Equipment.ROPE.url}),  # Default page
]
