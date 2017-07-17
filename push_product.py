import sys
import MySQLdb
import json
import time
import subprocess
from woocommerce import API
from os.path import basename, splitext
from logger import *

reload(sys)
sys.setdefaultencoding('utf8')

wcapi = API(
	url="http://example.com", # Your store URL
	consumer_key="ck_xxx", # Your consumer key
	consumer_secret="cs_xxx", # Your consumer secret
	wp_api=True, # Enable the WP REST API integration
	version="wc/v2", # WooCommerce WP REST API version
	timeout=100
)

product = {
	"name": "",
	"type": "simple",
	"regular_price": "0",
	"description": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante. Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. Mauris placerat eleifend leo.",
	"short_description": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.",
	"categories": [
		{
			"id": 1
		}
	],
	"images": [
		{
			"src": "",
			"position": 0
		},
		{
			"src": "",
			"position": 1
		}
	]
}

category = {
	"name": "",
	"image": {
		"src": ""
	}
}

MAX_TRY=3
LOG_NAME = "push_product.log"
logger = logger(LOG_NAME)

def handle_wcapi(base, data, checkcondition):
	global MAX_TRY
	trycnt = 0
	while trycnt < MAX_TRY:
		try:
			result = wcapi.post(base, data).json()
			if checkcondition in result:
				return True, result
			else:
				trycnt = trycnt + 1
		except:
			trycnt = trycnt + 1
			time.sleep(3)
	return False, -1


def log_data(result, cid, pid = -1, info = None):
	global logger
	msg = "[%s][%s] %s" % (str(cid), str(pid), str(info))
	logger.write_log(msg, loglevel.ALL, result)

def create_category(name):
	global category
	category["name"] = name
	result, info = handle_wcapi("products/categories", category, "id")
	if result:
		log_data(1, info["id"], -1, name)
		return info["id"]
	else:
		print "Failed to create category %s" % name
		log_data(0, -1, -1, name)
		return -1

def delete_product(pid):
	wcapi.delete("products/%d?force=true" % pid).json()

def delete_all_product():
	cats = wcapi.get("products/categories?per_page=100").json()
	for cat in cats:
		print "Deleting cat %s" % cat["name"]
		product = wcapi.get("products?category=%d" % cat["id"]).json()
		for p in product:
			wcapi.delete("products/%d?force=true" % p["id"]).json()
		wcapi.delete("products/categories/%d?force=true" % cat["id"]).json()


def create_product(cat_id, web_cat_id, cursor):
	global product
	global wcapi

	cursor.execute("SELECT * FROM sanpham WHERE secid = %d " % cat_id)
	products = cursor.fetchall()
	for row in products:
		cursor.execute("SELECT * FROM file WHERE secid = %d" % row[0])
		images = cursor.fetchall()
		product["images"] = []
		img_cnt = 0
		for img in images:
			imgs = {"src": "http://mytindigital.com/" + img[2], "position": img_cnt}
			product["images"].append(imgs)
			img_cnt = img_cnt + 1
		if count(product["images"]) > 0:
			product["name"] = row[2]
			product["regular_price"] = str(row[3])
			product["categories"][0]["id"] = web_cat_id
			product["description"] = row[8]
			product["short_description"] = row[7]
			result, info = handle_wcapi("products", product, "message")
			if result:
				log_data(1, web_cat_id, info["id"], info["permalink"])
				print "Success create product %s" % info["permalink"]
				# Wait for download image
				time.sleep(1)
			else:
				log_data(1, web_cat_id, row[0], row[2])
				print "Failed for id = %d" % row[0]


def push_product():
	db = MySQLdb.connect("localhost","root","123456","mytin" )
	cursor = db.cursor()
	cursor.execute("SET NAMES utf8")
	cursor.execute("SELECT * FROM danhmucsanpham")
	categories = cursor.fetchall()
	for row in categories:
		web_cat_id = create_category(row[2])
		if web_cat_id != -1:
			create_product(row[0], web_cat_id, cursor)


if __name__ == "__main__":
	push_product()