from django.db import models

class Addressee(models.Model):
    name = models.TextField()
    address = models.TextField()
    def __unicode__(self):
        return self.address

class Mail(models.Model):
    sender = models.ForeignKey(Addressee, related_name='sent_mails')
    to = models.ManyToManyField(Addressee, related_name='received_mails')
    cc = models.ManyToManyField(Addressee, related_name='cced_mails')
    subject = models.TextField()
    date = models.DateTimeField()
    message_id = models.TextField()
    thread_index = models.TextField()
    body = models.TextField()
    def __unicode__(self):
        return self.date.isoformat() + ' ' + self.sender.address[0:20] + ' ' + self.subject[0:30]