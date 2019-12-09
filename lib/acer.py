from .scraper import *
from .laptop_helper import LaptopHelper

class Acer(Scraper):
	#########################
	#
	#    GET DATA
	#
	#########################
	@catch_exception
	@data_file_exists_decorator
	def get_data(self,query):
		pass
	#########################
	#
	#    ORGANIZE DATA
	#
	#########################
	@catch_exception
	def organize_data(self):
		pass
	#########################
	#
	#    CONVERT DATA
	#
	#########################
	@catch_exception
	def convert_data(self):
		pass