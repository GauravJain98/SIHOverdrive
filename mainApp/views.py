from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
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


#     ps = ProblemStatement.objects.filter(ps_number=ps_number).first()
#     ps.ps_number = line['ps_number']
#     ps.description = line['description']
#     ps.youtube = line['youtube']
#     ps.title = line['title']
#     ps.organization = line['organization']
#     ps.category = line['category']
#     ps.domain_bucket = line['domain_bucket']
#     ps.img = line['img']
#     ps.save()
# else:
def function():
    from mainApp.models import ProblemStatement
    import csv
    reader = csv.DictReader(open("data-090120.csv"))
    for line in reader:
        # print("description,youtube,title,organization,category,ps_number,domain_bucket,img,")
        ps_number = line['ps_number']
        print(ps_number)
        try:
            if not ProblemStatement.objects.filter(ps_number=ps_number).exists():
                # ProblemStatement.objects.create(**line)
                print("wtf" + ps_number)
            # break
        except:
            print("ERROR {}".format(ps_number))

# def img_update():
#     from mainApp.models import ProblemStatement
#     reader = open("s-img-data.csv", "r")
#     data = reader.read().split("\n")
#     for line in data:
#         try:
#             ps_number, img = line.split(",")
#             try:
#                 ps = ProblemStatement.objects.get(ps_number=ps_number)
#                 ps.img = img
#                 ps.save()
#             except:
#                 print(ps_number)
#         except:
#             print(line)

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

    # def get(self, request, format=None):
    #     return Response("WORKS {request.user}")

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
            try:
                team = Team.objects.filter(archived=False).get(key=key)
            except Team.DoesNotExist:
                return Response("Invalid Key", status=status.HTTP_404_NOT_FOUND)
            if not Teammate.objects.filter(team=team, team_member=request.user.team_member, archived=False).exists():
                try:
                    req = Request.objects.get(team=team, team_member=request.user.team_member)
                    req.archived = False
                    req.save()
                    return Response("Request Already Sent Awaiting Response", status=status.HTTP_200_OK)
                except Request.DoesNotExist:
                    obj = Request(team=team, team_member=request.user.team_member)
                    obj.save()
                    return Response("Request Sent", status=status.HTTP_200_OK)
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


class ListProblems(AuthViewSet):

    def get(self, request, format=None):
        problem_statements = ProblemStatement.objects.all()
        serializer = ProblemStatementSerializer(problem_statements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def validateURL(url):
    validate = URLValidator()
    if url is None:
        return True
    try:
        validate(url)
        return True
    except ValidationError:
        return False


class ProblemTeam(AuthViewSet):

    def get(self, request, pk, format=None):
        team_id = request.GET.get("team", None)
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response("Invalid Team", status=status.HTTP_404_NOT_FOUND)
            if team and Teammate.objects.filter(team=team, team_member__user=request.user).exists():
                problem_statement_team = ProblemStatementTeam.objects.get(team=team, problem_statement=pk)
                serializer = ProblemStatementTeamSerializer(problem_statement_team)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)

    def patch_validate_data(self, request):
        error_data = {}
        data = {}
        error = False
        ps_read = request.data.get("read", None)
        ps_status = request.data.get("status", None)
        ps_document = request.data.get("document", None)
        ps_presentation = request.data.get("presentation", None)
        if ps_status:
            if ps_status not in ["Selected", "Neutral", "Rejected", "In-Progress"]:
                error = True
                error_data['status'] = f'Should be in [{", ".join(["Selected", "Neutral", "Rejected", "In-Progress"])}]'
            else:
                data['status'] = ps_status
        if ps_read is not None:
            if not isinstance(ps_read, bool):
                error = True
                error_data['read'] = 'Should be boolean'
            else:
                data['read'] = ps_read
        if ps_document:
            if not validateURL(ps_document):
                error = True
                error_data['document'] = 'Should be a valid url'
            else:
                data['document'] = ps_document
        if ps_presentation:
            if not validateURL(ps_presentation):
                error = True
                error_data['presentation'] = 'Should be valid url'
            else:
                data['presentation'] = ps_presentation
        data['error'] = error
        data['error_data'] = error_data
        return data

    def patch(self, request, pk, format=None):
        team_id = request.data.get("team", None)
        validated_data = self.patch_validate_data(request)
        error = validated_data.pop('error')
        if error:
            return Response(validated_data['error_data'], status=status.HTTP_400_BAD_REQUEST)
        else:
            validated_data.pop('error_data')
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response("Invalid Team", status=status.HTTP_404_NOT_FOUND)
            if team and Teammate.objects.filter(team=team, team_member__user=request.user).exists():
                problem_statement_team = ProblemStatementTeam.objects.filter(team=team, problem_statement=pk)

                problem_statement_team.update(**validated_data)
                serializer = ProblemStatementTeamSerializer(problem_statement_team.first())
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)


class ListProblemTeam(AuthViewSet):

    def get(self, request, format=None):
        team_id = request.GET.get("team", None)
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response("Invalid Team", status=status.HTTP_404_NOT_FOUND)
            if team and Teammate.objects.filter(team=team, team_member__user=request.user).exists():
                problem_statement_team = ProblemStatementTeam.objects.filter(team=team)
                serializer = ProblemStatementTeamSerializer(problem_statement_team, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)


class TeamMemberList(AuthViewSet):

    def get(self, request, pk, format=None):
        if pk is not None and Teammate.objects.filter(archived=False).filter(team__id=pk,
                                                                             team_member=request.user.team_member).exists():
            team_members = Teammate.objects.filter(archived=False).filter(team__id=pk)
            serializer = TeammateTeamMemberSerializer(team_members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)

    # Remove this to this url if change the url
    def patch(self, request, pk, format=None):
        teammates = Teammate.objects.filter(team__pk=pk, team_member=request.user.team_member, archived=False)
        note = request.data.get("note", None)
        name = request.data.get("name", None)
        if teammates.exists():
            teammate = teammates.first()
            if teammate.leader:
                team = teammate.team
                if note:
                    team.note = note
                if name:
                    team.name = name
                team.save()
            return Response("You aint the team leader bro", status=status.HTTP_200_OK)
        return Response("Not your team bro :(", status=status.HTTP_401_UNAUTHORIZED)

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


class ListProblemsCount(AuthViewSet):

    def get(self, request, format=None):
        return Response(ProblemStatement.objects.count(), status=status.HTTP_200_OK)


class ListCommentCount(AuthViewSet):

    def get(self, request, pk):
        team_id = request.GET.get("team", None)
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response("Invalid Team", status=status.HTTP_404_NOT_FOUND)
            if team and Teammate.objects.filter(team=team, team_member__user=request.user).exists():
                problem_statement_team = ProblemStatementTeam.objects.filter(team=team, problem_statement=pk)
                if problem_statement_team.exists():
                    comments = problem_statement_team.first().comments
                    return Response(comments.count(), status=status.HTTP_200_OK)
                return Response("Contact Developer", status=status.HTTP_404_NOT_FOUND)
            return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)


class ListComment(AuthViewSet):

    def get(self, request, pk):
        team_id = request.GET.get("team", None)
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response("Invalid Team", status=status.HTTP_404_NOT_FOUND)
            if team and Teammate.objects.filter(team=team, team_member__user=request.user).exists():
                problem_statement_team = ProblemStatementTeam.objects.filter(team=team, problem_statement=pk)
                if problem_statement_team.exists():
                    comments = problem_statement_team.first().comments
                    serializer = CommentSerializer(comments.all(), many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response("Contact Developer", status=status.HTTP_404_NOT_FOUND)
            return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        team_id = request.data.get("team", None)
        comment_text = request.data.get("comment", None)
        if team_id is not None:
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response("Invalid Team", status=status.HTTP_404_NOT_FOUND)
            teammates = Teammate.objects.filter(team=team, team_member__user=request.user)
            if team and teammates.exists():
                teammate = teammates.first()
                problem_statement_team = ProblemStatementTeam.objects.filter(team=team, problem_statement=pk)
                if problem_statement_team.exists():
                    comment = Comment.objects.create(problem_statement_team=problem_statement_team.first(),
                                                     teammate=teammate,
                                                     comment=comment_text)
                    serializer = CommentSerializer(comment)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response("Contact Developer", status=status.HTTP_404_NOT_FOUND)
            return Response("Not your team bro", status=status.HTTP_401_UNAUTHORIZED)
        errors = {}
        if team_id is None:
            errors['team'] = "Add Team Id"
        if comment_text is None:
            errors['comment'] = "Add Comment"
        return Response("Invalid Format", status=status.HTTP_400_BAD_REQUEST)
