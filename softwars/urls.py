from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework.authtoken import views as rest_auth_views
from django.conf import settings
from mainApp import views

# router = routers.DefaultRouter()
# router.register(r'teammate', views.TeammateViewSet)
# router.register(r'problemstatement', views.ProblemStatementViewSet)
# router.register(r'note', views.NoteViewSet)
# router.register(r'problemstatementteam', views.ProblemStatementTeamViewSet)
# router.register(r'comment', views.CommentViewSet)

# DONE
# PS static
# PS dyan
# Read
# Status
# New statement poll
# Comment and polling variable
# Team name update
# Requests

# TODOK
# Changed Password
# Add email service


urlpatterns = [
    url('api/register/', views.RegisterView.as_view()),
    url('api/register/', views.RegisterView.as_view()),
    url('api/team/list/', views.ListTeams.as_view()),
    # URL should be team_members
    url(r'api/team/(?P<pk>\d+)/$', views.TeamMemberList.as_view()),
    url('api/team/', views.JoinView.as_view()),
    url('api/notification/', views.NotificationView.as_view()),
    # URL should be user
    url('api/teammember/', views.TeamMemberViewSet.as_view()),
    url('api/god-admin/', admin.site.urls),
    url('api/login/', rest_auth_views.obtain_auth_token),
    url('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('api/problem_statement/count/', views.ListProblemsCount.as_view()),
    url('api/problem_statement/list/', views.ListProblems.as_view()),
    url(r'api/problem_statement/(?P<pk>\d+)/$', views.ProblemTeam.as_view()),
    url(r'api/comment/count/(?P<pk>\d+)/$', views.ListCommentCount.as_view()),
    url(r'api/comment/(?P<pk>\d+)/$', views.ListComment.as_view()),
    url('api/problem_statement/data/$', views.ListProblemTeam.as_view()),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
