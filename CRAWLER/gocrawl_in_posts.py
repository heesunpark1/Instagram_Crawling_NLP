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
import random
from bs4 import BeautifulSoup

try:
	from urlparse import urljoin
	from urllib import urlretrieve
except ImportError:
	from urllib.parse import urljoin, quote
	from urllib.request import urlretrieve

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# import pymongo
import logging
import datetime

from timeout import timeout

import sqlite3
from sqlite3 import Error

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

POST_REMOVE = '''
if('undefined' !== typeof arguments && arguments[0] > 0){
	var ele = document.getElementsByClassName('_ac7v');
	var prnt = ele[ele.length-1].parentNode;
	
	for(var i=0; i<arguments[0]; i++){
		var temp_ele = document.getElementsByClassName('_ac7v');
		console.log(temp_ele[0]);
		
		setTimeout(() => temp_ele[0].parentNode.removeChild(temp_ele[0].parentNode.firstChild), 1000);
		
		setTimeout(() => window.scrollTo(0, document.body.scrollHeight), 300);
		setTimeout(() => window.scrollTo(0, 0), 300);
	}
}
'''

class InstagramCrawler(object):
	"""
		Crawler class
	"""
	def __init__(self, headless=True, setting_path='settings.json'):
		# Setting
		with open(setting_path) as data_file:
			self.setting = json.load(data_file)

		# options = Options()
		options = webdriver.ChromeOptions()

		if headless:
			options.add_argument('--headless')
			options.add_argument('--disable-gpu')  # Last I checked this was necessary.

		options.add_argument('--no-sandbox')
		options.add_argument('--single-process')
		options.add_argument('--disable-dev-shm-usage')

		mobile_emulation = {"deviceName": "Samsung Galaxy S20 Ultra"}

		options.add_experimental_option("mobileEmulation", mobile_emulation)

		self._driver = webdriver.Chrome("/Users/andrewsohn/DEV/03.INSTALLED_APP/chromedriver", chrome_options=options)

		self._driver.implicitly_wait(10)
		self.data = defaultdict(list)

		try:
			self.conn = sqlite3.connect("../crawl_db.db")
			self.cur = self.conn.cursor()

		except Error as e:
			print(e)

		# DB connection
		# connection = pymongo.MongoClient(self.setting['DB_HOST'], self.setting['DB_PORT'])
		# db_name = self.setting['DB_NAME']
		# self.db = connection[db_name]
		# collectionName = "in-explore-{}-Collection".format(now.strftime("%Y-%m-%d"))
		# self.collection = self.db[collectionName]

	def crawl(self, csv_file_loc, query, crawl_type, authentication, is_random):
		print("crawl_type: {}, authentication: {}, is_random: {}"
			.format(crawl_type, authentication, is_random))

		# !! CHANGE FROM DB CONNECTION TO FILE SYSTEM !!

		self.csv_file_loc = csv_file_loc

		self.crawl_type = crawl_type
		self.is_random = is_random

		if is_random:
			self.query = random.choice(self.setting["HASHTAGS"])
		else:
			self.query = query

		self.crawl_type = crawl_type
		self.accountIdx = 0
		self.refresh_idx = 0

		self.login(authentication)
		self.browse_target_page()

		#Quit driver
		print("Quitting driver...")
		self.quit()

	def login(self, authentication=None):
		"""
			authentication: path to authentication json file
		"""
		self._driver.get(urljoin(self.setting['INSTA_DOMAIN'], "accounts/login/"))

		if authentication:
			print("Username and password loaded from {}".format(authentication))
			# print("Username and password loaded from {}".format(authentication))
			with open(authentication, 'r') as fin:
				self.auth_dict = json.loads(fin.read())

			# Input username
			try:
				username_input = WebDriverWait(self._driver, 5).until(
					EC.presence_of_element_located((By.NAME, 'username'))
				)
				username_input.send_keys(self.auth_dict["INSTAGRAM"][self.accountIdx]['username'])
			except Exception:
				self._driver.save_screenshot('img/{}'.format('screenshot_login_01.png'))

			# Input password
			try:
				password_input = WebDriverWait(self._driver, 5).until(
					EC.presence_of_element_located((By.NAME, 'password'))
				)
				password_input.send_keys(self.auth_dict["INSTAGRAM"][self.accountIdx]['password'])

				# Submit
				password_input.submit()
			except Exception:
				self._driver.save_screenshot('img/{}'.format('screenshot_login_02.png'))

		else:
			print("Type your username and password by hand to login!")
			print("You have a minute to do so!")

		try:
			later_btn = WebDriverWait(self._driver, 3).until(
				EC.presence_of_element_located(
					(By.CSS_SELECTOR, "div.cmbtv button.sqdOP"))
			)
			later_btn.click()

		except Exception:
			pass

		# WebDriverWait(self._driver, 60).until(
		# 	EC.presence_of_element_located((By.CSS_SELECTOR, CSS_EXPLORE))
		# )

	def quit(self):
		"""
			Exit Method
		"""
		self._driver.quit()

	def browse_target_page(self):
		self.cur.execute('''
		
		SELECT
			a.*
		FROM InstagramPostsIDOnly a
		LEFT JOIN InstagramPosts b
		ON a.id = b.id
			AND a.hash_tag = b.hash_tag
		WHERE
			a.hash_tag=?
			AND b.id IS NULL;
		    ''', (self.query,))

		for i, row in enumerate(self.cur.fetchall()):
			post_id = row[0]

			target_url = urljoin(self.setting['INSTA_DOMAIN'], f"/p/{row[0]}/")
			try:
				self._driver.get(target_url)

				try:
					see_more = WebDriverWait(self._driver, 3).until(
						EC.presence_of_element_located((By.CSS_SELECTOR, "div._aasx div._aat6 span._aacl span div[role='button']"))
					)
					see_more.click()

				except Exception:
					pass

				single_post = WebDriverWait(self._driver, 3).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, "div._aasx div._aat6 span._aacl span._aacl"))
				)

			except Exception:
				self._driver.save_screenshot('img/{}'.format('screenshot_post_error.png'))
				print('error occur !!!!!!!!')

			try:
				print('[ ', i + 1, ' ] ',
					  {
						  "id": post_id
						  , "text": single_post.text
						  , "hash_tag": self.query
					  })

				self.cur.execute("INSERT INTO InstagramPosts (id, text, hash_tag) VALUES (?, ?, ?)",
								 (post_id, single_post.text, self.query))

				self.conn.commit()

			except (Error, Exception) as e:
				print(e)

		self.conn.close()

		# # Browse Hashtags
		# if hasattr(self, 'query'):
		# 	if self.is_random:
		# 		self.query = self.query.strip('#')
		#
		# 	query = quote(self.query.encode("utf-8"))
		#
		# 	relative_url = urljoin('explore/tags/', query.strip('#'))
		#
		# else:  # Browse user page
		# 	relative_url = "explore"
		#
		# target_url = urljoin(self.setting['INSTA_DOMAIN'], relative_url)
		#
		# self._driver.get(target_url)

	def nextAuth(self):
		self.accountIdx = 0 if len(self.auth_dict["INSTAGRAM"])-1 == self.accountIdx else self.accountIdx+1

	def logoutAndLogin(self):
		self._driver.get(urljoin(self.setting['INSTA_DOMAIN'], "accounts/logout"))

		self._driver.get(urljoin(self.setting['INSTA_DOMAIN'], "accounts/login/"))

		print("Since Instagram provides 5000 post views per Hour, relogin with annother username and password loaded from {}".format(authentication))

		# Input username
		try:
			username_input = WebDriverWait(self._driver, 5).until(
				EC.presence_of_element_located((By.NAME, 'username'))
			)
			username_input.send_keys(self.auth_dict["INSTAGRAM"][self.accountIdx]['username'])

		except Exception:
			self._driver.save_screenshot('img/{}'.format('screenshot_relogin_01.png'))

		# Input password
		try:
			password_input = WebDriverWait(self._driver, 5).until(
				EC.presence_of_element_located((By.NAME, 'password'))
			)
			password_input.send_keys(self.auth_dict["INSTAGRAM"][self.accountIdx]['password'])
			# Submit
			password_input.submit()

		except Exception:
			self._driver.save_screenshot('img/{}'.format('screenshot_relogin_02.png'))

		WebDriverWait(self._driver, 60).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, CSS_EXPLORE))
		)

	def scrape_photo_links(self, is_hashtag=False):
		print("Scraping photo links...")
		encased_photo_links = re.finditer(r'src="([https]+:...[\/\w \.-]*..[\/\w \.-]*'
								r'..[\/\w \.-]*..[\/\w \.-].jpg)', self._driver.page_source)

		photo_links = [m.group(1) for m in encased_photo_links]
		print(photo_links,"pprint")
		# begin = 0 if is_hashtag else 1

	def download_and_save(self, dir_prefix, query, crawl_type):
		# Check if is hashtag
		dir_name = query.lstrip(
			'#') + '.hashtag' if query.startswith('#') else query

		dir_path = os.path.join(dir_prefix, dir_name)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)

		print("Saving to directory: {}".format(dir_path))

		# Save Photos
		for idx, photo_link in enumerate(self.data['photo_links'], 0):
			sys.stdout.write("\033[F")
			print("Downloading {} images to ".format(idx + 1))
			# Filename
			_, ext = os.path.splitext(photo_link)
			filename = str(idx) + ext
			filepath = os.path.join(dir_path, filename)
			# Send image request
			urlretrieve(photo_link, filepath)

		# Save Captions
		for idx, caption in enumerate(self.data['captions'], 0):

			filename = str(idx) + '.txt'
			filepath = os.path.join(dir_path, filename)

			with codecs.open(filepath, 'w', encoding='utf-8') as fout:
				fout.write(caption + '\n')

		# Save followers/following
		filename = crawl_type + '.txt'
		filepath = os.path.join(dir_path, filename)
		if len(self.data[crawl_type]):
			with codecs.open(filepath, 'w', encoding='utf-8') as fout:
				for fol in self.data[crawl_type]:
					fout.write(fol + '\n')

def main():
	#   Arguments  #
	parser = argparse.ArgumentParser(description='Instagram Crawler')
	parser.add_argument('-d', '--csv_file_loc', type=str,
		default='./data/', help='directory to save results')
	parser.add_argument('-q', '--query', type=str,
		help="target to crawl, add '#' for hashtags")
	parser.add_argument('-t', '--crawl_type', type=str,
		default='all', help="Options: 'all' | 'tags' | 'photos'")
	parser.add_argument('-l', '--headless', action='store_true',
		help='If set, will use PhantomJS driver to run script as headless')
	parser.add_argument('-a', '--authentication', type=str, default='auth.json',
		help='path to authentication json file')
	parser.add_argument('-s', '--setting', type=str, default='settings.json',
		help='path to setting json file')
	parser.add_argument('-e', '--env', type=str, default='pro',
		help="environment options: 'pro' | 'dev' | 'test'")
	parser.add_argument('-r', '--random', action='store_true',
		help='enables tags mode with random hashtags @ setting.json')

	args = parser.parse_args()
	#  End Argparse #
	crawler = InstagramCrawler(headless=args.headless, setting_path = args.setting)
	crawler.crawl(csv_file_loc=args.csv_file_loc,
		query=args.query,
		crawl_type=args.crawl_type,
		authentication=args.authentication,
		is_random=args.random)

if __name__ == "__main__":
	main()