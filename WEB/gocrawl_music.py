from __future__ import division

import argparse
import codecs
from collections import defaultdict
import json
import csv
import os
import re
import sys
import asyncio
import time
from konlpy.tag import Kkma, Twitter
from bs4 import BeautifulSoup

try:
    from urlparse import urljoin
    from urllib import urlretrieve
except ImportError:
    from urllib.parse import urljoin, quote
    from urllib.request import urlretrieve

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.serializers import MusicTagSerializer, MusicTagPlaylistSerializer
from django.db.utils import IntegrityError
import datetime

# SELENIUM CSS SELECTOR
CSS_LOAD_MORE = "a._1cr2e._epyes"
CSS_RIGHT_ARROW = "a[class='_de018 coreSpriteRightPaginationArrow']"
FIREFOX_FIRST_POST_PATH = "//div[contains(@class, '_8mlbc _vbtk2 _t5r8b')]"
TIME_TO_CAPTION_PATH = "../../../div/ul/li/span"

# FOLLOWERS/FOLLOWING RELATED
CSS_EXPLORE_MAIN = "main._8fi2q._2v79o"
CSS_EXPLORE = "a[href='/explore/']"
CSS_EXPLORE_MAIN_LIST = "article._gupiw"
CSS_LOGIN = "a[href='/accounts/login/']"
CSS_FOLLOWERS = "a[href='/{}/followers/']"
CSS_FOLLOWING = "a[href='/{}/following/']"
FOLLOWER_PATH = "//div[contains(text(), 'Followers')]"
FOLLOWING_PATH = "//div[contains(text(), 'Following')]"

# JAVASCRIPT COMMANDS
SCROLL_UP = "window.scrollTo(0, 0);"
SCROLL_DOWN = "window.scrollTo(0, document.body.scrollHeight);"

POST_REMOVE = "if('undefined' !== typeof arguments && arguments[0] > 0){ \
 var ele = document.getElementsByClassName('_70iju'); \
 var prnt = ele[ele.length-1].parentNode; \
 for(var i=0; i<arguments[0]; i++){ \
 var temp_ele = document.getElementsByClassName('_70iju'); \
 temp_ele[0].parentNode.removeChild(temp_ele[0].parentNode.firstChild); \
 } \
 }"
# POST_REMOVE = "if('undefined' !== typeof arguments && arguments[0] > 0){ \
#  var ele = document.getElementsByClassName('_70iju'); \
#  var prnt = ele[ele.length-1].parentNode; \
#  for(var i=0; i<arguments[0]; i++){ \
#  var temp_ele = document.getElementsByClassName('_70iju'); \
#  console.log(arguments[0], temp_ele);\
#  temp_ele[0].parentNode.removeChild(temp_ele[0].parentNode.firstChild); \
#  } \
#  }"

now = datetime.datetime.now()


class MusicCrawler(object):
    """
        Crawler class
    """

    def __init__(self, headless=True, setting_path='settings.json'):
        # Setting
        with open(setting_path) as data_file:
            self.setting = json.load(data_file)

        if headless:
            self._driver = webdriver.PhantomJS(self.setting['PHANTOMJS_PATH'])
            self._driver.set_window_size(1120, 550)
        else:
            self._driver = webdriver.Firefox()

        self._driver.implicitly_wait(10)
        self.data = defaultdict(list)

    def crawl(self, query, crawl_type):
        self.query = query
        self.crawl_type = crawl_type
        self.browse_target_page()
        self.musicTags = []

        try:
            if crawl_type == "tags":
                self.getTagPlaylist(self.query)
            else:
                self.scrape_tags()
        except TimeoutException:
            # print("Quitting driver...")
            self.quit()

        # print("Quitting driver...")
        self.quit()

    def quit(self):
        """
            Exit Method
        """
        self._driver.quit()

    def browse_target_page(self):
        # Browse Hashtags
        if self.crawl_type == 'tags':
            query = quote(self.query.encode("utf-8"))
            relative_url = query.strip('#')

        self._driver.get(urljoin(self.setting['MUSIC_SITE_DOMAIN'], "playlist/tags"))

    def getTagPlaylist(self, tagCode):
        self._driver.get(urljoin(self.setting['MUSIC_SITE_DOMAIN'], "playlist/tags") + "?tags=" + tagCode)

        plList = WebDriverWait(self._driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "ul.recom-list"))
        )

        # self._driver.find_elements_by_css_selector("ul.recom-list")

        plList = BeautifulSoup(plList.get_attribute("innerHTML"), "html.parser")
        plLis = plList.findAll('li', class_='type_1')

        # while :
        # 추후 게시판 1 초과 페이지 목록 크롤링 작업


        for plLi in plLis:
            titleAtag = plLi.select('div.title a[href]')
            # <div class ="title" > < a href="#" onclick="javascript:goDetailView('5251'); return false;" > 즐거운 주말엔 신나는 아이돌 댄스 음악으로 기분 UP! < / a > < / div >
            # code = serializers.CharField(max_length=6, allow_blank=False)
            # title = serializers.CharField(max_length=40, allow_blank=False)
            # ext_tags = serializers.CharField(max_length=100, allow_blank=True)
            # url = serializers.CharField(max_length=100, allow_blank=False)
            onclick = titleAtag[0]["onclick"]

            # code = re.search(r"\b'[0-9]{4,}'\b", onclick)
            code = [int(s) for s in onclick.split('\'') if s.isdigit()][0]
            # code = re.search(r"\bjavascript: goDetailView\('(.*)'\); return false;\b", onclick)

            title = titleAtag[0].find(text=True, recursive=False)
            url = urljoin(self.setting['MUSIC_SITE_DOMAIN'], "playlist/detailView") + "?plmSeq=" + str(code)

            extTagList = plLi.select('div.tag a[href]')
            extTagArr = [tagA.find(text=True, recursive=False) for tagA in extTagList]
            ext_tags = ' '.join(extTagArr)

            mtpSerial = MusicTagPlaylistSerializer(data={"code": self.musicTags[-1][0]
                , "title": title, "url": url, "ext_tags": ext_tags })

            print(title, code, url, ext_tags)

            if mtpSerial.is_valid():
                row = mtpSerial.validated_data

                try:
                    mtpSerial.save()
                except IntegrityError:
                    pass

                self.musicTagsPlaylist.append(row['code'])



    def scrape_tags(self):
        """
            scrape_tags method : scraping Instagram image URL & tags
        """

        tagCont = WebDriverWait(self._driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "#body-content .tag-wrap .tag-mix"))
        )

        tagCont = BeautifulSoup(tagCont.get_attribute("innerHTML"), "html.parser")
        sentTagCont = tagCont.findAll('span', class_='group_4')[0]
        sentTagDl = sentTagCont.parent.parent
        sentTaga = sentTagDl.findAll('a', class_='tag-key')

        for aTag in sentTaga:
            onclick = aTag.get("onclick")
            code = re.search(r'\bSB[0-9]{4,}\b', onclick).group(0)
            sent = aTag.find(text=True, recursive=False)

            mtSerial = MusicTagSerializer(data={"code": code
                    , "sent": sent})
            print(code, sent)

            if mtSerial.is_valid():
                row = mtSerial.validated_data

                try:
                    mtSerial.save()
                    self.musicTags.append((row['code'], row['sent']))
                except IntegrityError:
                    self.musicTags.append((row['code'], row['sent']))
                    pass

                self.pageNum = 0
                self.musicTagsPlaylist = []

                self.getTagPlaylist(row['code'])

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Crawler')
    parser.add_argument('-t', '--crawl_type', type=str,
        default='all', help="Options: 'all' | 'tags'")
    parser.add_argument('-q', '--query', type=str,
                        help="target to crawl, add '#' for hashtags")
    parser.add_argument('-l', '--headless', action='store_true',
                        help='If set, will use PhantomJS driver to run script as headless')
    parser.add_argument('-s', '--setting', type=str, default='settings.json',
                        help='path to setting json file')
    args = parser.parse_args()
    #  End Argparse #
    
    crawler = MusicCrawler(headless=args.headless, setting_path=args.setting)
    crawler.crawl(query=args.query,
                  crawl_type=args.crawl_type)

if __name__ == "__main__":
    main()