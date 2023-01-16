from __future__ import division

import argparse
from subprocess import STDOUT, call, TimeoutExpired
import os
# import pymongo
import datetime
import json
import csv

GO_CRAWL_CMD = "python3"
GO_CRAWL_IN_PATH = "{}/gocrawl_in.py".format(os.path.dirname(os.path.abspath(__file__)))
GO_CRAWL_IN_ACO_PATH = "{}/gocrawl_in_aco.py".format(os.path.dirname(os.path.abspath(__file__)))
GO_CRAWL_FB_PATH = "{}/gocrawl_fb.py".format(os.path.dirname(os.path.abspath(__file__)))


def csv_len(fname):
    with open(fname) as f:
        csvreader = csv.reader(f)

        row_count = sum(1 for row in csvreader)

    return row_count


def main():
    #   Arguments  #
    parser = argparse.ArgumentParser(description='Pengtai Instagram Crawler')
    parser.add_argument('-d', '--dir_prefix', type=str,
                        default='./data', help='directory to save results')
    parser.add_argument('-q', '--query', type=str,
                        help="target to crawl, add '#' for hashtags")
    parser.add_argument('-t', '--crawl_type', type=str,
                        default='all', help="Options: 'all' | 'tags' | 'photos' | 'acousers'")
    parser.add_argument('-n', '--number', type=int, default=0,
                        help='Number of posts to download: integer')
    parser.add_argument('-k', '--sns_kind', type=str,
                        default='in', help="Options: 'in' | 'fb'")
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

    # VARIABLES #
    now = datetime.datetime.now()
    DIR_PREFIX = "{}/".format(os.path.dirname(os.path.abspath(__file__)))
    setting = None

    if args.sns_kind == 'in':
        if args.crawl_type == 'acousers' or args.crawl_type == 'users':
            GO_CRAWL_PATH = GO_CRAWL_IN_ACO_PATH
        else :
            GO_CRAWL_PATH = GO_CRAWL_IN_PATH

    else :
        GO_CRAWL_PATH = GO_CRAWL_FB_PATH


    DB_CURRENT_CNT = 0

    loop_cnt = int(args.number / 500)

    # img directory check
    dir_path = os.path.join(DIR_PREFIX, 'img')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Setting
    with open(args.setting) as data_file:
        setting = json.load(data_file)

    # daily db post count check
    # DB connection
    # connection = pymongo.MongoClient(setting['DB_HOST'], setting['DB_PORT'])
    # db_name = setting['DB_NAME']
    # db = connection[db_name]
    # collectionName = "{}-explore-{}-Collection".format(args.sns_kind, now.strftime("%Y-%m-%d"))
    # collection = db[collectionName]
    # DB_CNT = collection.find({}).count()
    # DB_TOBE_CNT = DB_CNT+args.number

    # !! CHANGE FROM DB CONNECTION TO FILE SYSTEM !!
    DB_CNT = 0
    csv_filename = "{}-{}-{}".format(args.sns_kind, args.crawl_type, now.strftime("%Y-%m-%d"))
    csv_file_loc = "{}/{}.csv".format(args.dir_prefix, csv_filename)

    if os.path.exists(csv_file_loc):
        DB_CNT = csv_len(csv_file_loc)
    else:
        with open(csv_file_loc, 'w') as file:
            if args.crawl_type == 'acousers' or args.crawl_type == 'users':
                file.writelines("post_id,user_id,img,text,write_date,reg_date\n")
            else :
                file.writelines("id,img,text,has_tag,write_date,reg_date\n")

    DB_TOBE_CNT = DB_CNT + args.number

    while DB_TOBE_CNT > DB_CURRENT_CNT:
        # print(args.crawl_type)
        cmd_arr = [GO_CRAWL_CMD, GO_CRAWL_PATH,
                   '-d=' + csv_file_loc,
                   '-t=' + args.crawl_type,
                   '-n=' + str(500),
                   '-a=' + args.authentication,
                   '-s=' + args.setting,
                   '-e=' + args.env]

        if args.query:
            cmd_arr.append('-q={}'.format(args.query))
        elif args.random:
            cmd_arr.append('-r')

        if args.headless:
            cmd_arr.append('-l')

        # subprocess.call(cmd_arr)
        # try:
        call(cmd_arr)

        if args.sns_kind == 'in' and args.crawl_type == 'users':
            break
        # except TimeoutExpired as e:
        # 	continue
        # finally:
        # DB_CURRENT_CNT = collection.find({}).count()
        DB_CURRENT_CNT = csv_len(csv_file_loc)
    # for num in range(loop_cnt):


if __name__ == "__main__":
    main()