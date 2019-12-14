import random
import string

from django.db import transaction
from rest_framework import serializers

from .models import *


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(stringLength))


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

    def create(self, validated_data):
        team = Team(
            name=validated_data['name'],
            key=randomString()
        )
        team.save()
        return team


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = TeamMember
        fields = ('user', 'gender')

    @transaction.atomic
    def create(self, validated_data):
        if not TeamMember.objects.filter(user__username=validated_data['user']['username']).exists():
            user_data = validated_data.pop('user')
            user = UserSerializer.create(UserSerializer(), user_data)
            team_member, created = TeamMember.objects.get_or_create(user=user, **validated_data)
            return team_member

        raise serializers.ValidationError(validated_data)


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


class RequestSerializer(serializers.ModelSerializer):
    team = TeamSerializer(required=True)
    team_member = TeamMemberSerializer(required=True)

    class Meta:
        model = Request
        fields = '__all__'
