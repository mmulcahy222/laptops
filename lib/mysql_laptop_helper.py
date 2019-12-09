import MySQLdb
import MySQLdb.cursors
from itertools import chain

#part_number - model_number - sub_family - source 

#only has insert & update & query

class MySqlLaptopHelper():
	dbc = ("localhost","root","","laptop")
	def __init__(self):
		self.db = MySQLdb.connect(*self.dbc, cursorclass=MySQLdb.cursors.DictCursor)
		self.cursor = self.db.cursor()
		part_numbers = self.query('SELECT part_number FROM laptop')
		self.part_numbers = [row['part_number'] for row in part_numbers]
	def query(self,sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()
	#########################
	#    mysql.insert('laptop',part_number="GOON",model_number="GREE")
	#########################
	def insert(self,table = 'laptop', **kwargs):
		attributes = []
		values = []
		#########################
		#    Avoid Duplicates
		#########################
		part_number = kwargs.get('part_number')
		if kwargs.get('part_number') in self.part_numbers:
			# print("%s is already in the laptops table" % part_number)
			return
		for k,v in kwargs.items():
			attributes.append(str(k))
			values.append("'" + str(v) + "'")
		sql = "INSERT INTO %s (%s) VALUES (%s)" % (table,','.join(attributes),','.join(values))
		self.cursor.execute(sql)
		try:
			self.db.commit()
			print('%s row(s) inserted -----> %s' % (self.cursor.rowcount,sql))
		except:
			self.db.rollback()
	#########################
	#    mysql.update('laptop',source="GRELL",where="part_number = 'GOON'")
	#########################
	def update(self,table = 'laptop', **kwargs):
		if 'where' in kwargs:
			attributes = []
			values = []
			set_values = ''
			where_clause = kwargs.get('where','error')
			kwargs.pop("where")
			for k,v in kwargs.items():
				set_values += "%s='%s'," % (k,v)
			sql = "UPDATE %s SET %s WHERE %s " % (table,set_values.rstrip(','),where_clause)
			# print(sql)
			self.cursor.execute(sql)
			try:
				self.db.commit()
				# print('%s row(s) updated ----> (%s)'  % (self.cursor.rowcount,sql))
			except:
				self.db.rollback()
		else:
			pass
			# print("Nothing happened. Put in where clause")
	#########################
	#    NO DELETE IS IN HERE
	#########################
	def delete(self, table = 'laptop'):
		pass
