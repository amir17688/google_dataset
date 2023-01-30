import berrl as bl
import pandas as pd
import itertools


data=pd.read_csv('points_example.csv')

count=0
ind=0
while not count==8:
	count+=1
	# making table associated with a specific presicion
	newtable=bl.map_table(data,count,list=True)

	

	#taking output to table and reading back into memory
	newtable.to_csv('table'+str(count)+'.csv')
	newtable=pd.read_csv('table'+str(count)+'.csv')
	
	# taking new table from a dataframe to a list
	newtable=bl.df2list(newtable)
	
	# reading table to test into memory 
	testtable=pd.read_csv('table_datum/table'+str(count)+'.csv')

	# taking test table to list
	testtable=bl.df2list(testtable)

	# testing every row in tables for 
	for a,b in itertools.izip(newtable,testtable):
		if not a==b:
			ind=1
			print 'Row New: %s, Row Old: %s' % (a,b)

	if ind==0:
		print 'Table size: %s Test Passed' % count

	# now testing the square size return on each geohash to see that passes as well
	
	# getting old squares
	oldsquares=pd.read_csv('squares_datum/testsquares'+str(count)+'.csv')

	# getting new squares
	newsquares=pd.read_csv('squares'+str(count)+'.csv')

	# taking both to lists
	oldsquares=bl.df2list(oldsquares)
	newsquares=bl.df2list(newsquares)

	# testing every row in squares
	for a,b in itertools.izip(newsquares,oldsquares):
		if not a==b:
			ind=1
			print 'Row New: %s, Row Old: %s' % (a,b)

	if ind==0:
		print 'Square size: %s Test Passed' % count

if ind==0:
	print 'pipegeohash build passed'



