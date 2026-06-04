"""项目根路由"""
from django.contrib import admin
from django.urls import path, include

# 注意: property.urls 必须放在 Django admin 之前
# 否则 Django admin 会拦截所有 admin/ 开头的 URL
urlpatterns = [
    path('', include('property.urls')),
    path('django-admin/', admin.site.urls),
]
