from .scraper import *
from .laptop_helper import *
import re
import json
from bs4 import BeautifulSoup

class Icecat(Scraper):
	#########################
	#
	#    GET DATA
	#
	#########################
	@data_file_exists_decorator
	def get_data(self,**kwargs):
		queries = [kwargs.get('part_number'),kwargs.get('model_number')]
		for query in queries:
			#########################
			#    GET THROUGH WEBSITE
			#########################
			try:
				url = 'http://icecat.us/en/search/?keyword=' + query
				print("Searching in %s" % url)
				icecat_search_html = self.get_html('http://icecat.us/en/search/?keyword=' + query)
				bs_icecat_search_html = BeautifulSoup(icecat_search_html,'lxml')
				href = [a['href'] for a in bs_icecat_search_html.select(".titleSearch") if query[-7:].replace('-',' ').lower() in a.text.replace('-',' ').lower()][0]
				icecat_id = re.findall('\d+(?=.html)',href)[0]
				return get_html('http://live.icecat.biz/api/?shopname=openIcecat-live&lang=en&content=&icecat_id=' + icecat_id)
			except:
				pass
		#########################
		#    GET THROUGH AUTOCOMPLETE (no exception because it will make client iterate to next source)
		#########################
		autocomplete_response = get_html('http://icecat.us/us/search/autocomplete?query=' + query)
		autocomplete_js = json.loads(autocomplete_response)
		icecat_id = [node['id'] for node in autocomplete_js['products'][0] if query[-7].replace('-',' ').lower() in node['name'].replace('-',' ').lower()][0]
		return get_html('http://live.icecat.biz/api/?shopname=openIcecat-live&lang=en&content=&icecat_id=' + icecat_id)
	#########################
	#
	#    ORGANIZE DATA
	#
	#########################
	def organize_data(self,data):
		bs = BeautifulSoup(data,'lxml')
		data = bs.text
		js = json.loads(data)
		site_data_dict = {}
		feature_groups = js['data']['FeaturesGroups']
		for feature_group in feature_groups:
			for feature in feature_group['Features']:
				attribute = feature['Feature']['Name']['Value']
				attribute = attribute.lower().replace(" ","_")
				presentation_value = feature['PresentationValue']
				site_data_dict[attribute] = presentation_value
		general_info = js['data']['GeneralInfo']
		site_data_dict['title'] = dvkp(general_info,'Title')
		site_data_dict['brand'] = general_info['Brand']
		try:
			site_data_dict['url'] = general_info['Description']['URL']
		except:
			site_data_dict['url'] = 'None'
		site_data_dict['model_number'] = general_info['ProductName']
		try:
			site_data_dict['product_family'] = general_info['ProductFamily']['Value']
		except:
			site_data_dict['product_family'] = 'Laptop'
		return site_data_dict
	#########################
	#
	#    CONVERT DATA
	#
	#########################
	def convert_data(self,data,**kwargs):
		#graphics
		graphics = dvkp(data,'discrete_graphics_adapter_model') + ' ' + dvkp(data,'discrete_graphics_memory_type') + ' ' + dvkp(data,'audio_&_video_graphics_processor')
		graphics += "On Board Graphics - " + dvkp(data,'on-board_graphics_adapter_model') + ' ' + dvkp(data,'on-board_graphics_adapter_base_frequency') if dvkp(data,'on-board_graphics_adapter') == 'Y' else ''
		#sound 
		sound = ''
		sound += "Microphone" if len(dvkp(data,'built-in_microphone')) > 0 else ''
		sound += " Subwoofer" if len(dvkp(data,'built-in_subwoofer')) > 0 else ''
		#dimensions 
		dimensions = ''
		dimensions += inch_reformulator(dvkp(data,'height')) if len(dvkp(data,'height')) > 0 else ''
		dimensions += " x " + inch_reformulator(dvkp(data,'width')) if len(dvkp(data,'width')) > 0 else ''
		dimensions += " x " + inch_reformulator(dvkp(data,'depth')) if len(dvkp(data,'depth')) > 0 else ''

		fields = {
			'audio_features' : '',
			'battery_type' : dvkp(data,'battery_technology') + ' ' + dvkp(data,'battery_type'),
			'camera' : 'Front Camera' if len(dvkp(data,'front_camera')) > 0 else '',
			'category' : dvkp(data,'brand'),
			'dimensions' : dimensions,
			'display' : get_inside_parentheses(dvkp(data,'display_diagonal')) + ' (' + dvkp(data,'display_resolution') + ')',
			'expansion_slots' : dvkp(data,'compatible_memory_cards'),
			'external_ports' : 'USB 2.0 x %s, USB 3.0 x %s, USB 3.1 x %s, VGA x %s' % (dvkp(data,'usb_2.0','0'),dvkp(data,'usb_3.0','0'),dvkp(data,'usb_3.1','0'),dvkp(data,'uga','0')),
			'flash_cache' : '',
			'hard_drive' : conditional_format('HDD = %s',dvkp(data,'hard_drive_capacity')) + ' ' + conditional_format('SSD = %s',dvkp(data,'solid-state')),
			'hp_apps' : '',
			'id_mech_description' : '',
			'keyboard' : 'Backlit Keyboard' if dvkp(data,'keyboard_backlit') == 'Y' else 'Keyboard',
			'memory' : dvkp(data,'internal_memory'),
			'memory_max' : dvkp(data,'maximum_internal_memory'),
			'microprocessor' : dvkp(data,'processor_family'),
			'microprocessor_cache' : dvkp(data,'processor_cache') + ' ' + dvkp(data,'processor_cache'),
			'minimum_dimensions_(w_x_d_x_h)' : dimensions,
			'modelurl' : dvkp(data,'url'),
			'multimedia_drive' : dvkp(data,'optical_drive_type'),
			'name' : dvkp(data,'title'),
			'network_card' : dvkp(data,'ethernet_lan_data_rates'),
			'network_interface' : dvkp(data,'ethernet_lan_data_rates'),
			'operating_system' : dvkp(data,'operating_system'),
			'pc_card_slots' : '',
			'pointing_device' : dvkp(data,'pointing_device'),
			'power' : dvkp(data,'ac_adapter_power'),
			'power_supply_type' : conditional_format('HDD = %s',dvkp(data,'input_voltage')) + ' ' + conditional_format('HDD = %s',dvkp(data,'output_voltage')),
			'pre-installed_software' : '',
			'product_name' : dvkp(data,'title'),
			'product_number' : dvkp(data,'model_number'),
			'software_-_productivity_&_finance' : '',
			'software_included' : '',
			'sound' : sound,
			'subcategory' : dvkp(data,'product_family'),
			'subsubcategory' : dvkp(data,'product_family'),
			'url' : dvkp(data,'url'),
			'video_graphics' : graphics,
			'webcam' : 'Front Camera' if len(dvkp(data,'front_camera')) > 0 else '',
			'weight' : dvkp(data,'weight'),
			'whats_in_the_box' : '',
			'wireless_connectivity' : dvkp(data,'wi-fi_standards'),
			'wwan' : '',
		}
		csv_row = self.convert_to_row(fields)
		csv_row = [clean_cell(value) for value in csv_row]
		return csv_row
