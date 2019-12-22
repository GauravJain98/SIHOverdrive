from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken import views as rest_auth_views

from mainApp import views

router = routers.DefaultRouter()
router.register(r'teammate', views.TeammateViewSet)
router.register(r'problemstatement', views.ProblemStatementViewSet)
router.register(r'note', views.NoteViewSet)
router.register(r'problemstatementteam', views.ProblemStatementTeamViewSet)
router.register(r'comment', views.CommentViewSet)

# DONE
# PS static
# PS dyan
# Read
# Status

# TODO
# New statement poll
# URL
# Comment and polling variable

# Team name update
# Problem Statement Statistics

# Logo
# Changed Password
# Requests
# Add email service


urlpatterns = [
    url('api/register/', views.RegisterView.as_view()),
    url('api/register/', views.RegisterView.as_view()),
    url('api/team/list/', views.ListTeams.as_view()),
    url(r'api/team/(?P<pk>\d+)/$', views.TeamMemberList.as_view()),
    url('api/team/', views.JoinView.as_view()),
    url('api/notification/', views.NotificationView.as_view()),
    url('api/teammember/', views.TeamMemberViewSet.as_view()),
    url('api/admin/', admin.site.urls),
    url('api/login/', rest_auth_views.obtain_auth_token),
    url('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('api/problem_statement/list/', views.ListProblems.as_view()),
    url(r'api/problem_statement/(?P<pk>\d+)/$', views.ProblemTeam.as_view()),
    url('api/problem_statement/data/$', views.ListProblemTeam.as_view()),
    url('api/', include(router.urls)),
]
