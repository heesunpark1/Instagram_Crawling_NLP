> 고려대학교 컴퓨터정보통신대학원 :: 2017 빅데이터 응용 세미나1
> 
> 인스타그램 이미지&해쉬태그 데이터 기반 감성분석

인스타그램/페이스북 크롤러
===


Requires
------------------
 * `python 3`
 * `virtualenv`
 * `mongoDB 3.4.3`
 * `npm`
 * `phantomjs`
 * `requests>=2.13.0`
 * `selenium>=3.4.0`
 * `pymongo>=3.5.1`
 * `asyncio==3.4.3`

Notice
------------------
Mac환경에서는 먼저 아래의 brew 인스톨 커맨드를 통해서 `selenium`과 `geckodriver`라는 Gecko-based WebDriver 클라이언트를 설치한다.

	$ brew install selenium
	$ brew install geckodriver

Change Log
=====
 * `v 1.0.0`
	 * [start] app initiated
	 * [update] facebook crawling added


## Get Started:

### 1. Python 가상화 
	$ virtualenv -p python3 {YOUR APP NAME}
	
### 2. 가상환경 Activation
	$ source {YOUR APP NAME}/bin/activate

### 3. 패키지 인스톨
	$ cd {YOUR APP NAME}
	$ pip3 install -r requirements.txt

### 4. 가상 브라우저 PHANTOMJS 설치
	$ npm install --save phantomjs
	or
	$ npm install --save

### 4. Setup Config auth.json & settings.json
- auth.json : place your instagram ID & password
- settings.json : mongoDB & PhantomJS path setting

### 5. Start Crawling

#### Config Arguments
- Environment Options:
	- '-e', '--env'
	- values: 'pro' | 'dev' | 'test'
	- default: 'pro'
- Directory to save results: 
	- '-d', '--dir_prefix'
	- default: './data/'
- Target to crawl, add '#' for hashtags: 
	- '-q', '--query'
	- default: 'explore'
- Crawl Type Options: 
	- '-t', '--crawl_type'
	- values: 'tags' | 'photos' | 'followers' | 'following'
	- default: 'tags'
- Number of posts to download(integer): 
	- '-n', '--number'
	- default: 0
- Add this flag to download caption when downloading photos: 
	- '-c', '--caption'
- If set, will use PhantomJS driver to run script as headless: 
	- '-l', '--headless'
- path to authentication json file: 
	- '-a', '--authentication'
	- default: 'auth.json'
- path to setting json file: 
	- '-s', '--setting'
	- default: 'settings.json'


### 크롤링 메크로 명령어

> Headless browser Phantom.JS 사용 명령어	

	$ python3 crawlbot.py -n {Post_Number} -e {Environment} -l

> 파이어폭스 브라우져 사용 명령어

	$ python3 crawlbot.py -n {Post_Number} -e {Environment}

> 헤쉬태그 사용 시 명령어

	$ python3 crawlbot.py -n {Post_Number} -e {Environment} -t tags -q {Hashtag word}


### 크롤링 후 MongoDB CSV Export

#### Instagram Collection

	$ mongoexport --db {DATABASE_NAME} --out {CSV_DEST_PATH}/explore-2017-09-28-Collection.csv --type=csv --collection {COLLECTION_NAME} --fields "_id,id,img,text,reg_date"

#### Facebook Collection

	$ mongoexport --db {DATABASE_NAME} --out {CSV_DEST_PATH}/fb-explore-2017-09-28-Collection.csv --type=csv --collection {COLLECTION_NAME} --fields "_id,id,post_type,post_id,img,text,reg_date,write_utime,write_date"