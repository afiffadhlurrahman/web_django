from django.db import models


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
