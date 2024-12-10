from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from gallery import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('art/<int:art_id>/', views.art_detail, name='art_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='gallery/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:art_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/subtract/<int:art_id>/', views.subtract_from_cart, name='subtract_from_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
