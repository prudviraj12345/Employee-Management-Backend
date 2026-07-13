from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/', include('department.urls')),

    path('api/', include('employee.urls')),

    path('api/', include('email_service.urls')),

    path('api/', include('history.urls')),
    path('api/', include('authentication.urls')),
]