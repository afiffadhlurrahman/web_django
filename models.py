# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DatasetPublication(models.Model):
    id_pub = models.CharField(primary_key=True, max_length=25)
    nidn = models.ForeignKey(
        'Researcher', models.DO_NOTHING, db_column='nidn', blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, null=True)
    topic = models.ForeignKey(
        'Topic', models.DO_NOTHING, db_column='topic', blank=True, null=True)
    subtopic = models.ForeignKey(
        'Subtopic', models.DO_NOTHING, db_column='subtopic', blank=True, null=True)
    cite = models.CharField(max_length=10, blank=True, null=True)
    authors = models.CharField(max_length=2000, blank=True, null=True)
    keywords = models.CharField(max_length=1000, blank=True, null=True)
    abstract = models.CharField(max_length=2000, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    source_title = models.CharField(max_length=1000, blank=True, null=True)
    volume = models.CharField(max_length=100, blank=True, null=True)
    # Field name made lowercase.
    doi = models.CharField(
        db_column='DOI', max_length=100, blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataset_publication'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        'DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FundingSponsor(models.Model):
    id_fund = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'funding_sponsor'


class KeywordResearcher(models.Model):
    kr_id = models.CharField(primary_key=True, max_length=25)
    nidn = models.ForeignKey(
        'Researcher', models.DO_NOTHING, db_column='nidn', blank=True, null=True)
    keyword = models.CharField(max_length=50, blank=True, null=True)
    df = models.IntegerField(blank=True, null=True)
    idf = models.FloatField(blank=True, null=True)
    link_dbpedia = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keyword_researcher'


class KeywordSubtopic(models.Model):
    ks_id = models.CharField(primary_key=True, max_length=25)
    subtopic = models.ForeignKey(
        'Subtopic', models.DO_NOTHING, blank=True, null=True)
    keyword = models.CharField(max_length=50, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    link_dbpedia = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keyword_subtopic'


class KeywordTopic(models.Model):
    kt_id = models.CharField(primary_key=True, max_length=25)
    topic = models.ForeignKey(
        'Topic', models.DO_NOTHING, blank=True, null=True)
    keyword = models.CharField(max_length=50, blank=True, null=True)
    df = models.IntegerField(blank=True, null=True)
    idf = models.FloatField(blank=True, null=True)
    link_dbpedia = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keyword_topic'


class ResearchCenter(models.Model):
    id_rscc = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'research_center'


class ResearchImplement(models.Model):
    id_research2 = models.CharField(
        unique=True, max_length=25, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'research_implement'


class ResearchProject(models.Model):
    id_research = models.CharField(primary_key=True, max_length=25)
    id_scheme = models.ForeignKey(
        'ResearchScheme', models.DO_NOTHING, db_column='id_scheme', blank=True, null=True)
    id_rscc = models.ForeignKey(
        ResearchCenter, models.DO_NOTHING, db_column='id_rscc', blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'research_project'


class ResearchScheme(models.Model):
    id_scheme = models.CharField(primary_key=True, max_length=25)
    id_fund = models.ForeignKey(
        FundingSponsor, models.DO_NOTHING, db_column='id_fund', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'research_scheme'


class ResearchTeam(models.Model):
    nidn = models.OneToOneField(
        'Researcher', models.DO_NOTHING, db_column='nidn', primary_key=True)
    id_research = models.ForeignKey(
        ResearchProject, models.DO_NOTHING, db_column='id_research')
    status = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'research_team'
        unique_together = (('nidn', 'id_research'),)


class Researcher(models.Model):
    nidn = models.CharField(primary_key=True, max_length=25)
    id_univ = models.ForeignKey(
        'University', models.DO_NOTHING, db_column='id_univ', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    scholar_id = models.CharField(max_length=255, blank=True, null=True)
    sinta_id = models.CharField(max_length=255, blank=True, null=True)
    scopus_id = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'researcher'


class ResearcherPublication(models.Model):
    nidn = models.CharField(max_length=25, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    topic = models.CharField(max_length=25, blank=True, null=True)
    jumlah_judul = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'researcher_publication'


class Subtopic(models.Model):
    subtopic_id = models.CharField(primary_key=True, max_length=25)
    topic = models.ForeignKey(
        'Topic', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subtopic'


class Topic(models.Model):
    topic_id = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'topic'


class University(models.Model):
    id_univ = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'university'
