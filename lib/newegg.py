from .scraper import *
from .laptop_helper import *
import re
import json
from bs4 import BeautifulSoup

class Newegg(Scraper):
	#########################
	#
	#    GET DATA
	#
	#########################
	@data_file_exists_decorator
	def get_data(self,**kwargs):
		query = kwargs.get('model_number')
		newegg_search_url = 'https://www.newegg.com/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description='+query+'&N=-1&isNodeId=1'
		print("Searching in %s" % newegg_search_url)
		newegg_search_html = self.get_chrome_html(newegg_search_url,wait_time=6)
		bs_newegg_search_html = BeautifulSoup(newegg_search_html,'lxml')
		product_spec_url = [a['href'] for a in bs_newegg_search_html.select(".item-title") if query[-7:].replace('-',' ').lower() in a.text.replace('-',' ').lower()][0]
		print("Searching in %s" % product_spec_url)
		self.spec_url = product_spec_url
		return get_chrome_html(product_spec_url,wait_time=6)
	#########################
	#
	#    ORGANIZE DATA
	#
	#########################
	def organize_data(self,data):
		bs = BeautifulSoup(data,'lxml')
		dls = bs.select('fieldset dl')
		nodes = []
		newegg_dict = {}
		for label in dls:
			attribute = label.select('dt')[0].text.lower().replace(' ','_')
			value = label.select('dd')[0].text
			newegg_dict[attribute] = value
		return newegg_dict
	#########################
	#
	#    CONVERT DATA
	#
	#########################
	def convert_data(self,data,**kwargs):
		part_number = get_item(kwargs,'part_number')
		#memory
		try:
			memory = data['memory']
		except:
			memory = ''
		#graphics
		try:
			graphics = data['graphics_card'] + ' ' + data['graphic_type']
		except:
			graphics = ''
		#networking
		try:
			this
		except:
			pass
		#hard_drive_size
		try:
			hard_drive_size = data.get('hdd','n/a') + ' ' + data.get('hdd_rpm','') + ' ' + data.get('hdd_interface','') + dvkp(data,'hard_drive_capacity') + ' ' + dvkp(data,'storage') + ' ' + dvkp(data,'ssd') 
		except:
			pass
		fields = {
			'audio_features' : '',
			'battery_type' : dvkp(data,'battery') +  + dvkp(data,'battery_life',''),
			'camera' : dvkp(data,'webcam'),
			'category' : dvkp(data,'series'),
			'dimensions' : dvkp(data,'dimensions'),
			'display' : '%s (%s)' % (dvkp(data,'screen'),dvkp(data,'resolution')),
			'expansion_slots' : dvkp(data,'usb') + ' ' + dvkp(data,'video_port') + ' ' + dvkp(data,'hdmi') + ' ' + dvkp(data,'audio_port'),
			'external_ports' : dvkp(data,'external_ports'),
			'flash_cache' : '',
			'hard_drive' : hard_drive_size,
			'hp_apps' : '',
			'id_mech_description' : '',
			'keyboard' : dvkp(data,'keyboard','') + dvkp(data,'touchpad',''),
			'memory' : memory,
			'memory_max' : dvkp(data,'memory_speed'),
			'microprocessor' : get_item(re.findall('.*?(?=\()',dvkp(data,'microprocessor')),0,''),
			'microprocessor_cache' : dvkp(data,'cache'),
			'minimum_dimensions_(w_x_d_x_h)' : dvkp(data,'dimensions'),
			'modelurl' : self.spec_url,
			'multimedia_drive' : dvkp(data,'optical_drive'),
			'name' : dvkp(data,'product_name'),
			'network_card' : dvkp(data,'lan'),
			'network_interface' : dvkp(data,'communication') + ' ' + dvkp(data,'lan'),
			'operating_system' : dvkp(data,'operating'),
			'pc_card_slots' : '',
			'pointing_device' : dvkp(data,'keyboard','') + dvkp(data,'touchpad',''),
			'power' : '',
			'power_supply_type' : '',
			'pre-installed_software' : '',
			'product_name' : dvkp(data,'product_name'),
			'product_number' : part_number,
			'software_-_productivity_&_finance' : '',
			'software_included' : '',
			'sound' : '',
			'subcategory' : dvkp(data,'series') + ' ' + clean(dvkp(data,'model')),
			'subsubcategory' : dvkp(data,'series') + ' ' + clean(dvkp(data,'model')),
			'url' : self.spec_url,
			'video_graphics' : graphics,
			'webcam' : dvkp(data,'webcam'),
			'weight' : dvkp(data,'weight'),
			'whats_in_the_box' : '',
			'wireless_connectivity' : dvkp(data,'wlan'),
			'wwan' : '',
		}
		csv_row = self.convert_to_row(fields)
		csv_row = [clean_cell(value) for value in csv_row]
		return csv_row