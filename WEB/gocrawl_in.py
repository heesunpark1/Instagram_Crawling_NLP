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

from app.serializers import InstaSerializer
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


class InstagramCrawler(object):
    """
        Crawler class
    """

    def __init__(self, setting_path='settings.json'):
        # Setting
        with open(setting_path) as data_file:
            self.setting = json.load(data_file)

        # if headless:
        self._driver = webdriver.PhantomJS(self.setting['PHANTOMJS_PATH'])
        self._driver.set_window_size(1120, 550)
        # else:
        # self._driver = webdriver.Firefox()

        self._driver.implicitly_wait(10)
        self.data = defaultdict(list)

    # DB connection
    # connection = pymongo.MongoClient(self.setting['DB_HOST'], self.setting['DB_PORT'])
    # db_name = self.setting['DB_NAME']
    # self.db = connection[db_name]
    # collectionName = "in-explore-{}-Collection".format(now.strftime("%Y-%m-%d"))
    # self.collection = self.db[collectionName]

    def crawl(self, query, number):
        self.query = query
        self.accountIdx = 0
        self.totalNum = number
        self.browse_target_page()
        self.resultArr = []

        try:
            self.scrape_tags_aco(number)
        except TimeoutException:
            # print("Quitting driver...")
            self.quit()
            self.preprocess()
            return self.resultArr2

        # print("Quitting driver...")
        self.quit()
        self.preprocess()
        return self.resultArr2

    def preprocess(self):
        """
            ACO용 전처리 작업
        """
        kkma = Kkma()
        t = Twitter()
        newArr = []
        sentArr = []
        nounsArr = []
        tokens_ko = []
        index = 0

        self.resultArr = sorted(self.resultArr, key=lambda t: t[0], reverse=False)

        for data in self.resultArr:
            sentPosArr = kkma.pos(data[1])
            inArr = []
            for outA in sentPosArr:
                # for inA in outA:
                inArr.append("/".join(outA))

            morph_arr = t.morphs(data[1])
            morphWords = [word for word in morph_arr if not word in tokens_ko]
            for word in morphWords:
                if not word in nounsArr:
                    nounsArr.append(word)

            tokens_ko.extend(morphWords)

            newArr.append({"sentence": "", "words": morph_arr, "score": 0})

            index = index + 1
            sentArr.append(";".join(inArr))

        index = 0
        for eaSent in sentArr:
            sentiScore = 0
            for corp in settings.KOSAC:
                if eaSent.find(corp['ngram']) > -1:
                    if corp['max.value'] == 'NEG':
                        sentiScore = sentiScore - float(corp['max.prop'])
                    elif corp['max.value'] == 'POS':
                        sentiScore = sentiScore + float(corp['max.prop'])

            newArr[index]["sentence"] = eaSent
            newArr[index]["score"] = sentiScore

            index = index + 1

        self.resultArr2 = newArr

    def quit(self):
        """
            Exit Method
        """
        self._driver.quit()

    def browse_target_page(self):
        # Browse Hashtags
        query = quote(self.query.encode("utf-8"))
        relative_url = query.strip('#')

        target_url = urljoin(self.setting['INSTA_DOMAIN'], relative_url)

        self._driver.get(target_url)
        self._driver.save_screenshot("/Users/Andrew-MB/DEV/05.GIT/GSCIT-sns-sentiment/WEB/screenshot_test.png")

    def scrape_tags_aco(self, number):
        """
            scrape_tags method : scraping Instagram image URL & tags
        """

        last_post_num_pre = 0

        user_h1_tag = WebDriverWait(self._driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "h1._rf3jb"))
        )

        user_id = user_h1_tag.get_attribute("title")

        while last_post_num_pre < number:

            WebDriverWait(self._driver, 3).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[contains(@class, '_mck9w') and contains(@class,'_gvoze') and contains(@class,'_f2mse')]"))
            )

            user_post_list_new = self._driver.find_elements_by_xpath(
                "//div[contains(@class, '_mck9w') and contains(@class,'_gvoze') and contains(@class,'_f2mse')]")

            if len(user_post_list_new) < 1:
                self.quit()

            user_cur_post = user_post_list_new[last_post_num_pre].find_elements_by_xpath(".//a")[0]
            post_url = user_cur_post.get_attribute("href")

            post_url_arr = post_url.split('/')
            post_id = post_url_arr[len(post_url_arr) - 2]

            self._driver.get(post_url)

            single_post = WebDriverWait(self._driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//article[contains(@class, '_7hhq6')]"))
            )

            article_src = BeautifulSoup(single_post.get_attribute("innerHTML"), "html.parser")

            data_box = article_src.find('div', class_='_ebcx9')
            media_box = article_src.find('div', class_='_sxolz')

            write_date = data_box.find('time', class_='_p29ma').get('datetime')
            write_date_ymd = write_date.split('T')[0]

            ul = data_box.find('ul', class_='_b0tqa')
            li = ul.find_all('li')[0]

            cleanr = re.compile('<.*?>')
            text = re.sub(cleanr, '', str(li.span))

            media_src = media_box.find_all(['video', 'img'])[0].get('src')

            reg_date = datetime.datetime.now()

            instaSerial = InstaSerializer(data={"post_id": post_id
                , "user_id": user_id
                , "img": media_src
                , "text": text
                , "write_date": write_date
                , "reg_date": reg_date})

            if instaSerial.is_valid():
                row = instaSerial.validated_data

                # text preprocess
                row['text'] = re.sub(r'@\w+', '', row['text'])
                row['text'] = re.sub(
                    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '',
                    row['text'])
                row['text'] = re.sub(r'[\[]|[\]]', '', row['text'])
                row['text'] = re.sub(r'[\r]|[\n]', ' ', row['text'])
                row['text'] = re.sub(r'[.]|[ㆍ]', '', row['text'])
                row['text'] = re.sub(r'#', ' ', row['text'])

                row['write_date'] = datetime.datetime(int(row['write_date'][0:4]), int(row['write_date'][5:7]),
                                                      int(row['write_date'][8:10]),
                                                      int(row['write_date'][11:13]), int(row['write_date'][14:16]),
                                                      int(row['write_date'][17:19]))

                # csvwriter.writerow([post_id, user_id, media_src, text, write_date, reg_date])
                try:
                    instaSerial.save()
                    self.resultArr.append((row['write_date'], row['text']))
                except IntegrityError:
                    self.resultArr.append((row['write_date'], row['text']))
                    pass

            last_post_num_pre = last_post_num_pre + 1
            # print("user's post count : {} ---------------------------------".format(last_post_num_pre))
            self._driver.back()

    def nextAuth(self):
        self.accountIdx = 0 if len(self.auth_dict["INSTAGRAM"]) - 1 == self.accountIdx else self.accountIdx + 1

    # def logoutAndLogin(self):
    #     self._driver.get(urljoin(self.setting['INSTA_DOMAIN'], "accounts/logout"))
    #
    #     self._driver.get(urljoin(self.setting['INSTA_DOMAIN'], "accounts/login/"))
    #
    #     EnvPrint.log_info(
    #         "Since Instagram provides 5000 post views per Hour, relogin with annother username and password loaded from {}".format(
    #             authentication))
    #
    #     # Input username
    #     try:
    #         username_input = WebDriverWait(self._driver, 5).until(
    #             EC.presence_of_element_located((By.NAME, 'username'))
    #         )
    #         username_input.send_keys(self.auth_dict["INSTAGRAM"][self.accountIdx]['username'])
    #
    #     except Exception:
    #         self._driver.save_screenshot('img/{}'.format('screenshot_relogin_01.png'))
    #
    #     # Input password
    #     try:
    #         password_input = WebDriverWait(self._driver, 5).until(
    #             EC.presence_of_element_located((By.NAME, 'password'))
    #         )
    #         password_input.send_keys(self.auth_dict["INSTAGRAM"][self.accountIdx]['password'])
    #         # Submit
    #         password_input.submit()
    #
    #     except Exception:
    #         self._driver.save_screenshot('img/{}'.format('screenshot_relogin_02.png'))
    #
    #     WebDriverWait(self._driver, 60).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, CSS_EXPLORE))
    #     )

def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram Crawler')
    parser.add_argument('-q', '--query', type=str,
                        help="target to crawl, add '#' for hashtags")
    parser.add_argument('-n', '--number', type=int, default=0,
                        help='Number of posts to download: integer')
    parser.add_argument('-a', '--authentication', type=str, default='auth.json',
                        help='path to authentication json file')
    parser.add_argument('-s', '--setting', type=str, default='settings.json',
                        help='path to setting json file')

    args = parser.parse_args()
    #  End Argparse #

    crawler = InstagramCrawler(setting_path=args.setting)
    print(crawler.crawl(query=args.query,
                  number=args.number))


if __name__ == "__main__":
    main()