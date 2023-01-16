from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Instagram, SentAnalyzer, MusicTag, MusicTagPlaylist


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class AnalyzerSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return SentAnalyzer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

class InstaSerializer(serializers.Serializer):
    post_id = serializers.CharField(max_length=15, allow_blank=False)
    user_id = serializers.CharField(max_length=30, allow_blank=False)
    img = serializers.CharField(max_length=150, allow_blank=False)
    text = serializers.CharField(max_length=1000, allow_blank=False)
    write_date = serializers.CharField(max_length=30, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Instagram.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.post_id = validated_data.get('post_id', instance.post_id)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.img = validated_data.get('img', instance.img)
        instance.text = validated_data.get('text', instance.text)
        instance.write_date = validated_data.get('write_date', instance.write_date)
        instance.save()
        return instance

class MusicTagSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, allow_blank=False)
    sent = serializers.CharField(max_length=15, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return MusicTag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.code = validated_data.get('code', instance.code)
        instance.sent = validated_data.get('sent', instance.sent)
        instance.save()
        return instance

class MusicTagPlaylistSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, allow_blank=False)
    title = serializers.CharField(max_length=100, allow_blank=False)
    ext_tags = serializers.CharField(max_length=170, allow_blank=True)
    url = serializers.CharField(max_length=100, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return MusicTagPlaylist.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.code = validated_data.get('code', instance.code)
        instance.title = validated_data.get('title', instance.title)
        instance.extTags = validated_data.get('extTags', instance.extTags)
        instance.url = validated_data.get('url', instance.url)

        instance.save()
        return instance