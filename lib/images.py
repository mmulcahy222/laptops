
import os,sys,traceback,threading



#########################
#
#    Catch all exceptions for methods
#
#########################
def catch_exception(func):
	def func_wrapper(self,*args,**kwargs):
		try:
			# raise ValueError('A very specific bad thing happened')
			data = func(self,*args,**kwargs)
			return data
		except Exception:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			exc_text = str(exc_type) + ' ' + str(exc_obj) + ' ' + str(exc_tb.tb_lineno)
			# print("Exception for %s ----> %s" % ('',exc_text))
			#
			# MORE DETAILED
			#
			traceback.print_exc()
			# 
			return False
	return func_wrapper


#########################
#
#    A decorator that returns a file that exists already, or saves it in a folder so it won't have to be called again
#
#########################
def images_file_exists_decorator(func):
	def func_wrapper(self,*args,**kwargs):
		model_number = get_item(kwargs,'model_number')
		file_path = 'C:/makeshift/files/laptops/data/%s_images.html' % model_number
		#get contents from file if it exists
		if(os.path.isfile(file_path) == True):
			data = file_get_contents(file_path)
			print("%s characters read from %s" % (len(data),file_path))
			return data
		#actually run function
		data = func(self,*args,**kwargs)
		#write to file
		bytes_written = file_put_contents(file_path,data)
		print("%s bytes has been written to %s" % (bytes_written,file_path))
		return data
	return func_wrapper




#########################
#
#    Images Class
#
#########################
class Images():
	def __init__(self):
		self.file_path_icecat_data = 'C:/makeshift/files/laptops/data/%s_data.txt'
		self.file_path_image = 'C:/makeshift/files/laptops/images/%s/'
	#########################
	#
	#    Get Datas
	#
	#########################
	def get_data(self):
		pass
	#########################
	#
	# 	Organize Data (get image links)
	#
	#########################
	def organize_data(self):
		pass
	#########################
	#
	#    Save Images
	#
	#########################
	@catch_exception
	def save_images_thread(self,image_link,file_path_image_full):
		lh = self.lh
		file_put_image(image_link,file_path_image_full)
		print("%s -> %s" % (file_path_image_full, image_link))
	#########################
	#    	Put in part number as kwarg argument, to denote the file path
	#########################
	@catch_exception
	def save_images(self,**kwargs):
		lh = self.lh
		image_links = kwargs['image_links']
		model_number = get_item(kwargs,'model_number')
		part_number = get_item(kwargs,'part_number')
		threads_all = []
		#it's just the folder with the part number and slash (no image)
		file_path_image = self.file_path_image % part_number
		if os.path.isdir(file_path_image) == False:
			os.mkdir(file_path_image)
		for key,image_link in enumerate(image_links):
			file_path_image_full = file_path_image + str(key) + ".jpg"
			threads_all.append(threading.Thread(target=self.save_images_thread, args=(image_link,file_path_image_full)))
		for thread in threads_all:
			thread.start()
		for thread in threads_all:
			thread.join()	
