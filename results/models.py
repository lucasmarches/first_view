from django.db import models

class LinkSection1(models.Model):
    link = models.TextField()
    origin = models.TextField()
    measure = models.TextField()
    intro = models.TextField()

    def __str__(self):
        return self.field_name

class LinkSection2(models.Model):
    link = models.TextField()
    origin = models.TextField()
    measure = models.TextField()
    intro = models.TextField()

    def __str__(self):
        return self.field_name

class LinkSection3(models.Model):
    link = models.TextField()
    origin = models.TextField()
    measure = models.TextField()
    intro = models.TextField()

    def __str__(self):
        return self.field_name

class PublicJobs(models.Model):
    legal_intrument = models.TextField()
    job_giver = models.TextField()
    appointed = models.TextField()
    job = models.TextField()
    where = models.TextField()
    das_code = models.TextField()
    link = models.TextField()
    date = models.DateField()


    def __str__(self):
        return self.field_name

    class Meta:
        ordering = ['-date']

class CadeCases(models.Model):
    process_number = models.TextField()
    companies = models.TextField()
    operation = models.TextField()
    date = models.DateField()


    def __str__(self):
        return self.field_name

    class Meta:
        ordering = ['-date']
