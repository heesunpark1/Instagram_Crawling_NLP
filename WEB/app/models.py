from django.db import models

class SentAnalyzer(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
	reg_date = models.DateTimeField(auto_now_add=True)
	text = models.TextField(null=False, blank=False)

class Instagram(models.Model):
	post_id = models.CharField(max_length=15, null=False, blank=False)
	user_id = models.CharField(max_length=30, null=False, blank=False)
	img = models.CharField(max_length=150, null=True, blank=True)
	text = models.TextField(null=False, blank=False)
	write_date = models.CharField(max_length=30, null=True, blank=True)
	reg_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = (["user_id", "write_date"])
		unique_together = (("post_id", "user_id"),)

class MusicTag(models.Model):
	code = models.CharField(max_length=6, null=False, blank=False)
	sent = models.CharField(max_length=15, null=False, blank=False)
	class Meta:
		ordering = (["code"])
		unique_together = (("code"),)

class MusicTagPlaylist(models.Model):
	code = models.CharField(max_length=6, null=False, blank=False)
	title = models.CharField(max_length=100, null=False, blank=False)
	ext_tags = models.CharField(max_length=170, null=True, blank=True)
	url = models.CharField(max_length=100, null=True, blank=True)
	reg_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = (["code"])
		unique_together = (("code", "title"),)