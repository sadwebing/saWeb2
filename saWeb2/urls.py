"""saWeb2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib   import admin
from django.urls      import path
from django.conf.urls import include, url
from django.conf      import settings
from django.conf.urls.static import static

urlpatterns = [
    # django管理后台
    path('admin/', admin.site.urls),
    
    # 域名解析管理
    url(r'^domainns/', include('domainns.urls')),

    # 主页 telegram
    url(r'^detect/', include('detect.urls')),

    # 登陆控制及用户信息
    url(r'^', include('control.urls')),
    url(r'^control/', include('control.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
