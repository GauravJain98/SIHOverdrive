from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken import views as rest_auth_views

from mainApp import views

router = routers.DefaultRouter()
router.register(r'team', views.TeamViewSet)
router.register(r'teammember', views.TeamMemberViewSet)
router.register(r'teammate', views.TeammateViewSet)
router.register(r'problemstatement', views.ProblemStatementViewSet)
router.register(r'note', views.NoteViewSet)
router.register(r'problemstatementteam', views.ProblemStatementTeamViewSet)
router.register(r'comment', views.CommentViewSet)

urlpatterns = [
    url('join/', views.JoinView.as_view()),
    url('admin/', admin.site.urls),
    url('api-token-auth/', rest_auth_views.obtain_auth_token),
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
]
