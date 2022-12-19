from django.urls import include, path
from movies.api.v1 import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'movies', views.FilmworkViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('movies/', views.MoviesListApi.as_view()),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
