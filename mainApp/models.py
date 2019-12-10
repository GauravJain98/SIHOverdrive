from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CommonInfo(models.Model):
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self):
        self.archived = True
        super().save()

    class Meta:
        abstract = True


class Team(CommonInfo):
    name = models.CharField(max_length=100, null=False, blank=False)
    key = models.CharField(max_length=6, unique=True, null=False, blank=False)
    note = models.TextField()

    def __str__(self):
        return self.name


class TeamMember(CommonInfo):
    user = models.ForeignKey(to=User, related_name='team_member', on_delete=models.CASCADE)
    team = models.ManyToManyField(to=Team, related_name='team_member', through='Teammate')

    def __str__(self):
        return f"{self.user.id} in {self.team}"


class Teammate(CommonInfo):
    team = models.ForeignKey(to=Team, related_name='team_mate', on_delete=models.CASCADE)
    team_member = models.ForeignKey(to=TeamMember, related_name='team_mate', on_delete=models.CASCADE)
    leader = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team_member.id} in {self.team}"


class Organization(CommonInfo):
    name = models.CharField(max_length=200, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


CATEGORIES = [
    ("S", "Software"),
    ("H", "Hardware")
]


class ProblemStatement(CommonInfo):
    organization = models.ForeignKey(to=Organization, related_name='problem_statement', on_delete=models.CASCADE)
    category = models.CharField(choices=CATEGORIES, max_length=2)
    ps_number = models.CharField(max_length=6)
    title = models.CharField(max_length=900)
    domain_bucket = models.CharField(max_length=100)
    description = models.TextField()
    youtube_link = models.CharField(max_length=50)

    # dataset_link = models.CharField(max_length=)

    def __str__(self):
        return f"{self.title}"


class Note(CommonInfo):
    teammate = models.ForeignKey(Teammate, on_delete=models.CASCADE)
    problem_statement = models.ForeignKey(ProblemStatement, on_delete=models.CASCADE)
    note = models.TextField()


STATUS = [
    ("S", "Selected"),
    ("N", "Neutral"),
    ("R", "Rejected"),
    ("T", "Thinking"),
]


class ProblemStatementTeam(CommonInfo):
    problem_statement = models.ForeignKey(ProblemStatement, on_delete=models.CASCADE)
    team = models.ForeignKey(to=Team, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=30)


class Comment(CommonInfo):
    problem_statement_team = models.ForeignKey(ProblemStatementTeam, on_delete=models.CASCADE)
    teammate = models.ForeignKey(Teammate, on_delete=models.CASCADE)

    def clean(self):
        if self.teammate.team != self.problem_statement_team.team:
            raise ValidationError("Only team members can comment")
