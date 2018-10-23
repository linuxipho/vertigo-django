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
from django.contrib.auth import views as auth_views
from django.urls import path, re_path, include

from vertigo import views
from vertigo.models import Equipment

urlpatterns = [
    # Password reset URLs
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #         auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('login/', auth_views.LoginView.as_view(), name='custom_login'),
    path('admin/login/', auth_views.LoginView.as_view(template_name='registration/login.html')),
    path('logout/', views.logout_page, name='logout'),
    path('admin/', admin.site.urls),
    path('import/', views.import_page, name='import'),
    path('export/', views.export_pdf, name="export"),

    path('<slug:url_type>/accord/', views.agreement_page, name='agreement_url'),
    path('<slug:url_type>/', views.list_page, name='list_url'),
    path('<slug:url_type>/emprunt/id-<int:item_id>', views.borrowing_page, name='borrowing_url'),

    path('', views.list_page, {'url_type': Equipment.ROPE.url}, name='default'),  # Default page
]
