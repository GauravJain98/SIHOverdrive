from rest_framework import permissions
from rest_framework.permissions import BasePermission

from mainApp.models import Teammate


class CommentPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS and obj.teammate.team_member == request.user.team_member


class ProblemStatementTeamPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return Teammate.objects.filter(archived=False).filter(team=obj.team,
                                                              team_member=request.user.team_member).exists()
