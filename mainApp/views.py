from rest_framework import viewsets

from .serializers import *


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer


class TeammateViewSet(viewsets.ModelViewSet):
    queryset = Teammate.objects.all()
    serializer_class = TeammateSerializer


class ProblemStatementViewSet(viewsets.ModelViewSet):
    queryset = ProblemStatement.objects.all()
    serializer_class = ProblemStatementSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class ProblemStatementTeamViewSet(viewsets.ModelViewSet):
    queryset = ProblemStatementTeam.objects.all()
    serializer_class = ProblemStatementTeamSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
