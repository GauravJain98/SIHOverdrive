from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class TeamMemberPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and request.user.team_member == obj)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class TeamMemberViewSet(APIView):
    permission_classes = (TeamMemberPermission,)
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user.team_member).data, status=status.HTTP_200_OK)


class TeammateViewSet(viewsets.ModelViewSet):
    queryset = Teammate.objects.all()
    serializer_class = TeammateSerializer


class ProblemStatementViewSet(viewsets.ModelViewSet):
    queryset = ProblemStatement.objects.all()
    serializer_class = ProblemStatementSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class ProblemStatementTeamPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return Teammate.objects.filter(team=obj.team, team_member=request.user.team_member).exists()


class ProblemStatementTeamViewSet(viewsets.ModelViewSet):
    queryset = ProblemStatementTeam.objects.all()
    permission_classes = (ProblemStatementTeamPermission,)
    serializer_class = ProblemStatementTeamSerializer

    def get_queryset(self):
        request = self.request
        pst = ProblemStatementTeam.objects.filter(team__team_mate__team_member=request.user.team_member)
        return pst


class CommentPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS and obj.teammate.team_member == request.user.team_member


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (CommentPermission,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['problem_statement_team', 'teammate']


class RegisterView(CreateAPIView):
    permission_classes = ()
    serializer_class = TeamMemberSerializer


class JoinView(APIView):
    serializer_class = TeamSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response(f"WORKS {request.user}")

    def post(self, request, format=None):
        if request.data.get('create', "") == 'true':
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                team = serializer.save()
                Teammate.objects.get_or_create(team=team, team_member=request.user.team_member, leader=True)
                request.user.team_member.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            key = request.data['key']
            name = request.data['name']
            team = Team.objects.get(name=name, key=key)
            request = Request.objects.get_or_create(team=team, team_member=request.user.team_member)
            return Response("Request Sent", status=status.HTTP_200_OK)


class NotificationView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        team = request.GET['team']
        notifications = Request.objects.filter(accepted=False, team__id__in=request.user.team_member.team_mate.filter(
            leader=True).filter(id=team).values_list("team__id", flat=True))
        serializer = RequestSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        notification = request.data.get("notification", None)
        team_member = request.user.team_member
        teams = team_member.team.filter(team_mate__leader=True)
        if notification is not None:
            request_obj = Request.objects.get(id=notification, team__in=teams)
            request_obj.accepted = True
            request_obj.save()
            Teammate(team_member=request_obj.team_member, team=request_obj.team)
            return Response(f"Accepted {request_obj.team_member.user.first_name}", status=status.HTTP_400_BAD_REQUEST)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)


class ListTeams(APIView):
    def get(self, request, format=None):
        tm = request.user.team_member
        team = Teammate.objects.filter(team_member=tm)
        serializer = TeammateSerializer(team, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListProblem(APIView):
    def get(self, request, team, format=None):
        if Teammate.objects.filter(team__id=team, team_member=request.user.team_member):
            team = ProblemStatementTeam.objects.filter(team_id=team)
            serializer = ProblemStatementSerializer(team, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
