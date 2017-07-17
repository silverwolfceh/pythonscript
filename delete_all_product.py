import sys
import json
from woocommerce import API
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

def delete_all_product(logger = None):
	if not logger:
		logger = logger("delete_product.log")
	cats = wcapi.get("products/categories?per_page=100").json()
	for cat in cats:
		logger.write_log("Deleting products in category %s" % cat["name"], 1, True)
		print "Deleting products in category %s" % cat["name"]
		product = wcapi.get("products?category=%d" % cat["id"]).json()
		for p in product:
			wcapi.delete("products/%d?force=true" % p["id"]).json()
		logger.write_log("Deleting category", 1, True)
		print "Deleting category"
		wcapi.delete("products/categories/%d?force=true" % cat["id"]).json()

if __name__ == "__main__":
	logger = logger("delete_product.log")
	delete_all_product(logger)