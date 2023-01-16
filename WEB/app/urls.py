from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.urls import path, include
from rest_framework import routers
# admin.autodiscover()
from app.admin import admin_site
from app import views
# from crawls import views as cviews
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
	url(r'^analyze/$', views.AnalyzeView.as_view()),
    url(r'^analyze/predict/$', views.AnalyzePredictView.as_view()),
    url(r'^analyze/playlist/$', views.AnalyzePlaylistView.as_view()),
    # url(r'^analyze/monitor/log/$', views.CrawlMonitorView.as_view()),
    # url(r'^analyze/monitor/csvdata/$', views.CrawlCSVDataView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns.extend([
	# url(r'^$', views.MainView.as_view(), name='index'),
#     # url(r'^admin/', include(admin.site.urls)),
#     url(r'^', include(admin_site.urls)),
    path(r'', admin_site.urls),

   # path(r'^', admin_site.urls),
   # path('hello/', include('myapp.views')),

    url(r'^logout$', auth_views.auth_logout, {'next_page' : '/'}, name='logout'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
])