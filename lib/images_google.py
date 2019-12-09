from .images import *
import re
import json
import urllib
from bs4 import BeautifulSoup

class ImagesGoogle(Images):
	@catch_exception
	@images_file_exists_decorator
	#########################
	#
	#    Get Data
	#
	#########################
	def get_data(self,**kwargs):
		query = get_item(kwargs,'query')
		html = self.get_chrome_html('https://www.google.com/search?q='+query+'&source=lnms&tbm=isch')
		return html
	#########################
	#
	#    Organize Data
	#
	#########################
	@catch_exception
	def organize_data(self,data):
		lh = self.lh
		image_links = []
		data = urllib.parse.unquote_plus(data)
		html = BeautifulSoup(data,'lxml')
		a_els = html.select('.rg_di a')
		for a in a_els:
			href = a['href']
			image_link = get_item(dvkp(urllib.parse.parse_qs(href),'imgurl'),0)
			if 'http' in image_link:
				image_links.append(image_link)
		return image_links[:12]
