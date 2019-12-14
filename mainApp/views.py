from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


class CreateView(APIView):
    def post(self, request, format=None):
        serializer: object = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(CreateView):
    serializer_class = TeamMemberSerializer


class JoinView(APIView):
    serializer_class = TeamSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response(f"WORKS {request.user}")

    def post(self, request, format=None):
        if request.data.get('create', False) is True:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            key = request.data['key']
            try:
                team = Team.objects.get(key=key)
            except Team.DoesNotExist:
                raise ValidationError("Invalid key")
            request = Request.objects.get_or_create(team=team, team_member=request.user.team_member)
            return Response("Request Sent", status=status.HTTP_200_OK)
