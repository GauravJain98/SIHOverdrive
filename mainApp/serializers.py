from django.db import transaction
from rest_framework import serializers

from .models import *


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = TeamMember
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        if not TeamMember.objects.filter(user__username=validated_data['username']).exists():
            user_data = dict()
            user_data['username'] = validated_data.pop('username')
            user_data['password'] = validated_data.pop('password')
            user_data['email'] = validated_data.pop('email')
            UserSerializer.create(UserSerializer(), user_data)
            team_member = TeamMember.objects.get_or_create(user_data, **validated_data)
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
