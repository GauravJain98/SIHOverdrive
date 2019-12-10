from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

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
    url('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
