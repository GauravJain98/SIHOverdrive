from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save


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
    key = models.CharField(max_length=10, null=True, blank=True, unique=True)
    note = models.TextField(default="")

    def __str__(self):
        return self.name


GENDER = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]


class TeamMember(CommonInfo):
    avatar = models.CharField(max_length=10, null=True, blank=True, default="")
    user = models.OneToOneField(to=User, related_name='team_member', on_delete=models.CASCADE)
    team = models.ManyToManyField(to=Team, related_name='team_member', through='Teammate')
    gender = models.CharField(max_length=5, choices=GENDER, null=False)

    def __str__(self):
        return f"{self.user.email}"


class Teammate(CommonInfo):
    team = models.ForeignKey(to=Team, related_name='team_mate', on_delete=models.CASCADE)
    team_member = models.ForeignKey(to=TeamMember, related_name='team_mate', on_delete=models.CASCADE)
    leader = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team_member.id} in {self.team}"


CATEGORIES = [
    ("S", "Software"),
    ("H", "Hardware")
]


class ProblemStatement(CommonInfo):
    organization = models.CharField(max_length=200, null=False, blank=False, unique=True)
    category = models.CharField(choices=CATEGORIES, max_length=2)
    ps_number = models.CharField(max_length=6)
    title = models.CharField(max_length=900)
    domain_bucket = models.CharField(max_length=100)
    description = models.TextField()
    youtube = models.CharField(max_length=50)
    dataset_link = models.CharField(max_length=100)

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
    ("I", "In-Progress"),
]


class ProblemStatementTeam(CommonInfo):
    read = models.BooleanField(default=False)
    problem_statement = models.ForeignKey(ProblemStatement, on_delete=models.CASCADE)
    team = models.ForeignKey(to=Team, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=30)
    presentation = models.URLField()
    document = models.URLField()


class Comment(CommonInfo):
    problem_statement_team = models.ForeignKey(ProblemStatementTeam, on_delete=models.CASCADE)
    teammate = models.ForeignKey(Teammate, on_delete=models.CASCADE)

    def clean(self):
        if self.teammate.team != self.problem_statement_team.team:
            raise ValidationError("Only team members can comment")


class Request(CommonInfo):
    team = models.ForeignKey(to=Team, on_delete=models.CASCADE)
    team_member = models.ForeignKey(to=TeamMember, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)


def team_post(sender, instance, created, *args, **kwargs):
    for ps in ProblemStatement.objects.all():
        pst = ProblemStatementTeam.objects.create(problem_statement=ps, team=instance)
        pst.save()


def problem_statement_post(sender, instance, created, *args, **kwargs):
    for t in Team.objects.all():
        pst = ProblemStatementTeam.objects.create(problem_statement=instance, team=t)
        pst.save()


post_save.connect(problem_statement_post, sender=ProblemStatement)
post_save.connect(team_post, sender=Team)
