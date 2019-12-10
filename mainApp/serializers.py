from rest_framework import serializers

from .models import *


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'


class TeammateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teammate
        fields = '__all__'


class ProblemStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatement
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class ProblemStatementTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemStatementTeam
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
