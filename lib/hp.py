from .scraper import *
from .laptop_helper import *
import re
import json
from bs4 import BeautifulSoup

class Hp(Scraper):
	#########################
	#
	#    GET DATA
	#
	#########################
	@data_file_exists_decorator
	def get_data(self,**kwargs):
		query = kwargs.get('model_number')
		query = query.strip().lower()
		hp_search_url = 'http://www8.hp.com/us/en/search/search-results.html?ajaxpage=1#/page=1&/qt=' + query
		print("Searching in " + hp_search_url)
		hp_search_html = self.get_chrome_html(hp_search_url)
		bs_hp_search_html = BeautifulSoup(hp_search_html,'lxml')
		href = [a['href'] for a in bs_hp_search_html.select(".fade-title") if query[-7:].lower() in a.text.lower() if 'speci' in a.text.lower()][0]
		self.spec_url = href
		return get_html(href)
	#########################
	#
	#    ORGANIZE DATA
	#
	#########################
	def organize_data(self,data):
		bs = BeautifulSoup(data,'lxml')
		trs = bs.select('.table-bordered tr')
		nodes = []
		hp_dict = {}
		for row in trs:
			try:
				attribute = row.select('td')[0].text.lower().replace(' ','_').replace('\n', '').replace(' ','_')
				value = row.select('td')[1].text.replace('\n', '').replace('\r','')
				hp_dict[attribute] = value
			except:
				pass
		return hp_dict
	#########################
	#
	#    CONVERT DATA
	#
	#########################
	def convert_data(self,data,**kwargs):
		#memory
		memory_data =  get_inside_parentheses(dvkp(data,'microprocessor')).split(',')
		memory = get_item(re.findall("\d*?\.?\d*?\sGHz",get_item(memory_data,0)),0)
		memory_max = get_item(re.findall("\d*?\.?\d*?\sGHz",get_item(memory_data,1)),0)
		processor_cache = get_item(re.findall("\d*?\.?\d*?\sMB",get_item(memory_data,2)),0)
		fields = {
			'audio_features' : dvkp(data,'audio'),
			'battery_type' : dvkp(data,'battery_type'),
			'camera' : '',
			'category' : get_item(dvkp(data,'product_name').split(),1),
			'dimensions' : dvkp(data,'dimensions'),
			'display' : dvkp(data,'display'),
			'expansion_slots' : dvkp(data,'expansion_slots'),
			'external_ports' : dvkp(data,'external_ports'),
			'flash_cache' : '',
			'hard_drive' : dvkp(data,'hard_drive'),
			'hp_apps' : dvkp(data,'hp_apps'),
			'id_mech_description' : '',
			'keyboard' : dvkp(data,'keyboard'),
			'memory' : memory,
			'memory_max' : memory_max,
			'microprocessor' : get_item(re.findall('.*?(?=\()',dvkp(data,'microprocessor')),0),
			'microprocessor_cache' : processor_cache,
			'minimum_dimensions_(w_x_d_x_h)' : dvkp(data,'dimensions'),
			'modelurl' : self.spec_url,
			'multimedia_drive' : dvkp(data,'optical_drive'),
			'name' : dvkp(data,'product_name'),
			'network_card' : dvkp(data,'ethernet_lan_data_rates'),
			'network_interface' : dvkp(data,'network_interface'),
			'operating_system' : dvkp(data,'operating_system'),
			'pc_card_slots' : '',
			'pointing_device' : dvkp(data,'pointing_device'),
			'power' : dvkp(data,'power_supply_type'),
			'power_supply_type' : dvkp(data,'power_supply_type'),
			'pre-installed_software' : dvkp(data,'installed_software'),
			'product_name' : dvkp(data,'product_name'),
			'product_number' : dvkp(data,'product_number'),
			'software_-_productivity_&_finance' : dvkp(data,'finance'),
			'software_included' : dvkp(data,'software_included'),
			'sound' : dvkp(data,'audio_features'),
			'subcategory' : ' '.join(dvkp(data,'product_name').split()[:2]),
			'subsubcategory' : ' '.join(dvkp(data,'product_name').split()[:2]),
			'url' : self.spec_url,
			'video_graphics' : dvkp(data,'graphics'),
			'webcam' : dvkp(data,'webcam'),
			'weight' : dvkp(data,'weight'),
			'whats_in_the_box' : '',
			'wireless_connectivity' : dvkp(data,'wireless'),
			'wwan' : '',
		}
		csv_row = self.convert_to_row(fields)
		csv_row = [clean_cell(value) for value in csv_row]
		return csv_row
