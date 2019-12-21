from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from mainApp.models import Team, Note, Teammate, ProblemStatement, TeamMember, ProblemStatementTeam, Comment, Request
from mainApp.permissions import CommentPermission, ProblemStatementTeamPermission
from mainApp.serializers import TeamSerializer, NoteSerializer, TeammateSerializer, ProblemStatementSerializer, \
    TeamMemberSerializer, ProblemStatementTeamSerializer, CommentSerializer, TeammateTeamMemberSerializer, \
    RequestSerializer


class AuthViewSet(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticated,)


class TeamMemberPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and request.user.team_member == obj)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.filter(archived=False).all()
    serializer_class = TeamSerializer


class TeammateViewSet(viewsets.ModelViewSet):
    queryset = Teammate.objects.filter(archived=False).all()
    serializer_class = TeammateSerializer


class ProblemStatementViewSet(viewsets.ModelViewSet):
    queryset = ProblemStatement.objects.filter(archived=False).all()
    serializer_class = ProblemStatementSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.filter(archived=False).all()
    serializer_class = NoteSerializer


class TeamMemberViewSet(AuthViewSet):
    permission_classes = (TeamMemberPermission,)
    queryset = TeamMember.objects.filter(archived=False).all()
    serializer_class = TeamMemberSerializer

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user.team_member).data, status=status.HTTP_200_OK)


class ProblemStatementTeamViewSet(viewsets.ModelViewSet):
    queryset = ProblemStatementTeam.objects.filter(archived=False).all()
    permission_classes = (ProblemStatementTeamPermission,)
    serializer_class = ProblemStatementTeamSerializer

    def get_queryset(self):
        request = self.request
        pst = ProblemStatementTeam.objects.filter(archived=False).filter(
            team__team_mate__team_member=request.user.team_member)
        return pst


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (CommentPermission,)
    queryset = Comment.objects.filter(archived=False).all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['problem_statement_team', 'teammate']


class RegisterView(CreateAPIView):
    permission_classes = ()
    serializer_class = TeamMemberSerializer


class JoinView(AuthViewSet):
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
                Teammate.objects.filter(archived=False).get_or_create(team=team, team_member=request.user.team_member,
                                                                      leader=True)
                request.user.team_member.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            key = request.data['key']
            team = Team.objects.filter(archived=False).get(key=key)
            if Teammate.objects.filter(team=team, team_member=request.user.team_member).exists():
                request, created = Request.objects.filter(archived=False).get_or_create(team=team,
                                                                                        team_member=request.user.team_member)
                if created:
                    return Response("Request Sent", status=status.HTTP_200_OK)
                return Response("Request Already Sent Awaiting Response", status=status.HTTP_200_OK)
            return Response("Already Joined Team", status=status.HTTP_200_OK)


class NotificationView(AuthViewSet):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        team = request.GET['team']
        if Teammate.objects.filter(archived=False).filter(leader=True, team__id=team,
                                                          team_member=request.user.team_member).exists():
            notifications = Request.objects.filter(archived=False).filter(accepted=False, team__id=team)
            serializer = RequestSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Not team leader", status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, format=None):
        notification = request.data.get("notification", None)
        team_member = request.user.team_member
        teams = team_member.team.filter(team_mate__leader=True)
        if notification is not None:
            request_obj = Request.objects.filter(archived=False).get(id=notification, team__in=teams)
            request_obj.accepted = True
            request_obj.save()
            Teammate.objects.create(team_member=request_obj.team_member, team=request_obj.team, leader=False)
            return Response(f"Accepted {request_obj.team_member.user.first_name}", status=status.HTTP_200_OK)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        notification = request.data.get("notification", None)
        team_member = request.user.team_member
        teams = team_member.team.filter(archived=False).filter(team_mate__leader=True)
        if notification is not None:
            try:
                request_obj = Request.objects.filter(archived=False).get(id=notification, team__in=teams)
                request_obj.delete()
                return Response("Request Deleted", status=status.HTTP_200_OK)
            except:
                return Response("Request does not exist", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("No Notification ID", status=status.HTTP_400_BAD_REQUEST)


class ListTeams(AuthViewSet):

    def get(self, request, format=None):
        tm = request.user.team_member
        team = Teammate.objects.filter(archived=False).filter(team_member=tm)
        serializer = TeammateSerializer(team, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListProblem(AuthViewSet):

    def get(self, request, team, format=None):
        if Teammate.objects.filter(archived=False).filter(team__id=team, team_member=request.user.team_member):
            team = ProblemStatementTeam.objects.filter(archived=False).filter(team_id=team)
            serializer = ProblemStatementSerializer(team, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)


class TeamMemberList(AuthViewSet):

    def get(self, request, pk, format=None):
        if pk is not None and Teammate.objects.filter(archived=False).filter(team__id=pk,
                                                                             team_member=request.user.team_member).exists():
            team_members = Teammate.objects.filter(archived=False).filter(team__id=pk)
            serializer = TeammateTeamMemberSerializer(team_members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if pk is not None and Teammate.objects.filter(archived=False).filter(team__id=pk,
                                                                             team_member=request.user.team_member).exists():
            team_member = Teammate.objects.filter(archived=False).filter(team__id=pk,
                                                                         team_member=request.user.team_member).first()
            if team_member.leader is True:
                team_members = Teammate.objects.filter(archived=False).filter(team__id=pk).exclude(
                    id=team_member.id).first()
                if team_members is None:
                    Team.objects.filter(archived=False).filter(id=pk).delete()
                    return Response("Team Deleted", status=status.HTTP_200_OK)
                else:
                    team_members.leader = True
                    team_members.save()
            team_member.delete()
            return Response(f"Left team {team_member.team.name}", status=status.HTTP_200_OK)
        return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)
