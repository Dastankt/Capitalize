from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('', include('users.urls')),
    path('transactions/', include('transactions.urls')),
    path('goals/', include('goals.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)