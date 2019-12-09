from .images import *
import re
import json
from bs4 import BeautifulSoup


class ImagesIcecat(Images):
	#########################
	#
	#    Unique Method for this class (See if Data Sheet is an Icecat Sheet)
	#
	#########################
	@catch_exception
	def is_icecat_data(self,model_number):
		file_path_icecat_data = self.file_path_icecat_data % model_number
		try:
			if os.path.isfile(file_path_icecat_data) == True:
				data = file_get_contents(file_path)
				js = json.loads(data)
				gallery = js['data']['Gallery']
				if len(gallery) > 0:
					return True
				else:
					return False
			else:
				return False
		except e:
			return False
	#########################
	#
	#    Get Data
	#
	#########################
	@catch_exception
	def get_data(self,**kwargs):
		model_number = get_item(kwargs,'model_number')
		data = self.file_get_contents(self.file_path_icecat_data % model_number)
		return data
	#########################
	#
	#    Organize Data (RETURN A LIST OF LINKS)
	#
	#########################
	@catch_exception
	def organize_data(self,data):
		js = json.loads(data)
		image_links = []
		for image in js['data']['Gallery']:
			image_links.append(image['Pic'])
		return image_links
	