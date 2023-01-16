from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from rest_framework import viewsets, status
from app.serializers import UserSerializer, GroupSerializer, AnalyzerSerializer, InstaSerializer
from django.shortcuts import render
from django.views import View
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.conf import settings
import requests
from konlpy.tag import Kkma, Twitter
import time
import datetime
import pandas as pd
from .models import SentAnalyzer, MusicTag, MusicTagPlaylist
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from django.db.utils import IntegrityError

from bs4 import BeautifulSoup
import re

try:
    from urlparse import urljoin
    from urllib import urlretrieve
except ImportError:
    from urllib.parse import urljoin, quote
    from urllib.request import urlretrieve

from .mlLoad import *
global model

#initialize these variables
model = init()

url_pat = "((https?:\/\/)|(\/)|(..\/))(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?"
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

char_pattern1 = '[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]'
char_pattern2 = re.compile(
    "["
    "a-z"
    "A-Z"
    "0-9"
    "가-힣"
    "ㄱ-ㅎ"
    "ㅏ-ㅣ"
    "ぁ-ゔ"
    "一-龥"
    "]+")

class_texts = [
    "#기쁨",
    "#슬픔",
    "#즐거움",
    "#화남"
]
class_texts_pat = r'(?:{})'.format('|'.join(class_texts))

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# def (request):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#
#     return render(request, 'index.html', {'form': form})

# class MainView(View):
#     authentication_classes = (SessionAuthentication, BasicAuthentication)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         if not request.session.session_key:
#             return HttpResponseRedirect('/admin/')
#         # print(request.auth)

#         form = SentAnalyzerForm()
#         return render(request, 'index.html', {'form': form})

class AnalyzeView(APIView):
	parser_classes = (JSONParser,)
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		# print(request.user)

		analyz = SentAnalyzer.objects.all()
		serializer = AnalyzerSerializer(analyz, many=True)
		return Response(serializer.data)

class AnalyzePredictView(APIView):
	parser_classes = (JSONParser,)
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		serializer = AnalyzerSerializer(data=request.query_params)

		if serializer.is_valid():
			formData = serializer.validated_data

			############################ 			ML			###################################
			# with open("new_data.json", "r") as jf:
			# 	dt = json.load(jf)
			t = Twitter()

			trg_txt = formData['text']

			# 1. 공백 제거
			trg_txt = trg_txt.strip()
			trg_txt = ' '.join(trg_txt.splitlines())
			# print(f"1:::: {trg_txt}")

			# 2. URL 제거
			trg_txt = re.sub(url_pat, r'', trg_txt)

			# 3. emoji 제거
			trg_txt = emoji_pattern.sub(r'', trg_txt)
			# print(f"2:::: {trg_txt}")

			# 4. 감정 해시 태그 제거
			trg_txt = re.sub(class_texts_pat, r'', trg_txt)

			# 5. 특수문자 제거
			trg_txt = ' '.join(re.sub(char_pattern1, ' ', trg_txt).split())
			trg_txt = ' '.join(re.findall(char_pattern2, trg_txt))
			# print(f"3:::: {trg_txt}")

			trg_txt = ' '.join([w for w, _ in t.pos(trg_txt, norm=True)])

			inf_res = model.predict(trg_txt, k=3)
			print(inf_res)

			inf_classes = [_.replace('__label__', '') for _ in inf_res[0]]
			inf_acc = list(inf_res[1])

			############################# 			MUSIC RECOMMENDATION			###################################
			if inf_classes[0] == '긍정':
				highPredictVal = '기쁨'

			elif inf_classes[0] == '부정':
				highPredictVal = '슬픔'
			else:
				highPredictVal = ''

			if highPredictVal:
				predMusicTags = MusicTag.objects.filter(sent__contains=highPredictVal)
				# print(predMusicTags[0].code)

				musicTagPlaylistQs = MusicTagPlaylist.objects.filter(code__exact=predMusicTags[0].code)
				predMusicPlaylist = [playlist.url for playlist in musicTagPlaylistQs]
			else:
				predMusicPlaylist = []

			print(predMusicPlaylist)

			serializer.save()
			return Response({
				"ml": [serializer.data, inf_classes, inf_acc]
				, "history": []
				, "sentiKword": []
				, "playlist":predMusicPlaylist
			}, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnalyzePlaylistView(APIView):
	parser_classes = (JSONParser,)
	authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		print(request.query_params)
		resArr = []
		musicUrl = request.query_params['musicUrl']

		result = requests.get(musicUrl)
		htmlCont = BeautifulSoup(result.content)

		mlCont = htmlCont.findAll('div', class_='music-list-wrap')[0]
		mlTrs = mlCont.findAll('tr', class_='list')

		for mltr in mlTrs:
			titleTag = mltr.find('a', class_='title')
			# print(titleTag)

			cleanr = re.compile('<.*?>')
			title = re.sub(cleanr, '', str(titleTag))

			if "\n" in title:
				newLArr = title.split("\n")
				title = newLArr[-1]
			# title = titleTag.find(text=True, recursive=False)

			artistTag = mltr.find('a', class_='artist')
			artist = artistTag.find(text=True, recursive=False)

			albumtitleTag = mltr.find('a', class_='albumtitle')
			albumtitle = albumtitleTag.find(text=True, recursive=False)

			resArr.append({"title":title.strip(), "artist":artist.strip(), "albumtitle":albumtitle.strip()})

		print(resArr)
		return Response({ "songs":resArr }, status=status.HTTP_201_CREATED)