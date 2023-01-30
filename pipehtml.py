
import os
from pipegeojson import *
import json
import itertools

# experimenting with dierent popups
def make_rows(headers):
	varblock=[]
	# makes a list of rows from a given input header
	for row in headers:
		newrow='\t\t\t\t + "<br>%s:" + feature.properties.place' % (row)
		varblock.append(newrow)

	return varblock	

# the function actually used to make the styles table
def make_rows2(headers):
	varblock=[]
	# makes a list of rows from a given input header
	for row in headers:

		maxchared=15

		row1=row
		row2=row
		if row==headers[0]:
			newrow="""            var popupText = "<table><tr><th>%s: </th><td>" + feature.properties['%s']+"</td></tr>"; """ % (row1,row2)
		else:
			newrow="""            var popupText = popupText+ "<tr><th>%s: </th><td>" + feature.properties['%s']+"</td></tr>"; """ % (row1,row2)
		varblock.append(newrow)
		if row==headers[-1]:
			newrow="""            var popupText = popupText+ "<tr><th>%s: </th><td>" + feature.properties['%s']+</td></tr></table>"; """ % (row1,row2)
	return varblock	

# experimenting with dierent popups
def make_rows5(headers):
	varblock=[]
	# makes a list of rows from a given input header
	for row in headers:
		row1=row
		row2=row
		newrow="""            var popupText = "%s: " + feature.properties['%s']
""" % (row1,row2)
		varblock.append(newrow)


# experimenting with dierent popups
def make_rows3(headers):
	varblock=[]
	# makes a list of rows from a given input header
	for row in headers:
		row1='<tr><td>'+row+'<td>'
		row2=row
		if row==headers[0]:
			newrow="""            var popupText = "%s:" + feature.properties['%s']
	""" % (row1,row2)
		else:
			newrow="""            var popupText = popupText+ "%s: <td>" + feature.properties['%s']
	""" % (row1,row2)

		varblock.append(newrow)
		if row==headers[-1]:
			pass
	return varblock	

# experimenting with different popups
def make_rows4(headers):
	varblock=[]
	# makes a list of rows from a given input header
	for row in headers:
		varblock=['            var popupText = "<table width=1>"']
		row1=row
		row2=row
		if row==headers[0]:
			newrow="""            + "<p>%s:" + feature.properties['%s']+"<.p>"
	""" % (row1,row2)
		else:
			newrow="""            +"<td>%s:</td><td>" + feature.properties['%s']+"</td></tr>"
	""" % (row1,row2)
		if row==headers[-1]:
			newrow="""            +"<td>%s:</td><td>" + feature.properties['%s']+"</td></tr></table>"
	""" % (row1,row2)
		varblock.append(newrow)
		if row==headers[-1]:
			pass
	return varblock	

# makes the block str for all the unique data within the html file
def making_blockstr(varblock):
	start="""function addDataToMap(data, map) {
    var dataLayer = L.geoJson(data, {
        onEachFeature: function(feature, layer) {"""

	end="""
	            layer.bindPopup(popupText, {autoPan:false} ); }
        });
    dataLayer.addTo(map);\n}"""
    	total=''
    	for row in varblock:
    		total+=row
    	return start+total+end

# makes the style bindings for each element
def make_bindings(headers):
	varblock=make_rows2(headers)
	block=making_blockstr(varblock)	
	return block

# make_blockstr with color and elment options added (newer)
def making_blockstr2(varblock,count,colorline,element):
	start="""function addDataToMap%s(data, map) {
    var dataLayer = L.geoJson(data, {
        onEachFeature: function(feature, layer) {""" % count

	end="""
	            layer.bindPopup(popupText, {autoPan:false, maxHeight:500, maxWidth:350} ); }
        });
    dataLayer.addTo(map);\n}"""
    	total=''
    	for row in varblock:
    		total+=row
    	if element=='Point':
    		return start+total+colorline+end
    	else:
    		return start+total+'\n'+colorline+end

# make bindings after color options were added
def make_bindings2(headers,count,colorline,element):
	varblock=make_rows2(headers)
	block=making_blockstr2(varblock,count,colorline,element)	
	return block

#writes text file to given location 
def writetxt(data,location):
	with open(location,'w') as f:
		f.writelines(data)
	print 'Wrote text file to location %s' % location


# writes the html file to a document then opens it up in safari (beware it will call a terminal command)
def load(lines,filename):

	with open(filename,'w') as f:
		f.writelines(lines)

	f.close()	
	os.system('open -a Safari '+filename)

'''
# not used in current iteration of module
def make_all_headertype(header,geojsonlocations):

	a=make_html_block(header,geojsonlocations)

	writetxt(a,'a.html')
	#load(a,'a.html')
'''

# given a list of file names and kwargs carried throughout returns a string of the function bindings for each element
def make_bindings_type(filenames,color_input,colorkey,file_dictionary):
	string=''
	blocky="""\nfunction addDataToMap(data, map) {
    var dataLayer = L.geoJson(data);
    dataLayer.addTo(map);
}\n"""
	count=0
	for row in filenames:
		color_input=''
		count+=1
		filename=row
		with open(row) as data_file:    
   			data = json.load(data_file)
   		#pprint(data)
   		data=data['features']
   		data=data[0]
   		featuretype=data['geometry']
   		featuretype=featuretype['type']
		data=data['properties']
		if not file_dictionary==False:
			try:
				color_input=file_dictionary[filename]
			except Exception:
				color_input=''
			if featuretype=='Point':
				colorline=get_colorline_marker(color_input)
			else:
				colorline=get_colorline_marker2(color_input)

   		if not colorkey=='':
   			if featuretype=='Point':
   				colorline=get_colorline(data[str(colorkey)])
   			else:
   				colorline=get_colorline_marker2(data[str(colorkey)])

   		if featuretype=='Point':
   			colorline=get_colorline_marker(color_input)
   		else:
   			colorline=get_colorline_marker2(color_input)
   		

   		
   		headers=[]
   		for row in data:
   			headers.append(str(row))
   		blocky=	blocky="""\nfunction addDataToMap%s(data, map) {
    var dataLayer = L.geoJson(data);
    dataLayer.addTo(map);
}\n""" % count
		loc="""$.getJSON('http://localhost:8000/%s',function(data) { addDataToMap%s(data,map); });""" % (filename,count)
		if featuretype=='Point':
			string+=blocky+loc+make_bindings2(headers,count,colorline,featuretype)+'\n'
		else:
			string+=blocky+loc+make_bindings2(headers,count,colorline,featuretype)+'\n'
	return string


# makes the corresponding styled html for the map were about to load
def make_html(filenames,color_input,colorkey,apikey,file_dictionary,legend):
	block="""<html>
<head>
<meta charset=utf-8 />
<title>PipeGeoJSON Demo</title>
<meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
<script src="https://api.mapbox.com/mapbox.js/v2.2.4/mapbox.js"></script>


<script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>
<link href='https://api.mapbox.com/mapbox.js/v2.2.4/mapbox.css' rel='stylesheet' />
<style>
  body { margin:0; padding:0; }
  #map { position:absolute; top:0; bottom:0; width:100%; }
</style>
</head>
<body>
<style>
table, th, td {
    border: 1px solid black;
}
</style>


xxxxx


<script src='https://api.mapbox.com/mapbox.js/plugins/leaflet-omnivore/v0.2.0/leaflet-omnivore.min.js'></script>

<div id='map'></div>

<script>
L.mapbox.accessToken = 'pk.eyJ1IjoibXVycGh5MjE0IiwiYSI6ImNpam5kb3puZzAwZ2l0aG01ZW1uMTRjbnoifQ.5Znb4MArp7v3Wwrn6WFE6A';
var map = L.mapbox.map('map', 'mapbox.streets',{
    center: [38, -102.0],
    zoom: 5
    });

// omnivore will AJAX-request this file behind the scenes and parse it: 

// note that there are considerations:
// - The file must either be on the same domain as the page that requests it,
//   or both the server it is requested from and the user's browser must
//   support CORS.

// Internally this uses the toGeoJSON library to decode the KML file
// into GeoJSON





\n""".replace('pk.eyJ1IjoibXVycGh5MjE0IiwiYSI6ImNpam5kb3puZzAwZ2l0aG01ZW1uMTRjbnoifQ.5Znb4MArp7v3Wwrn6WFE6A',apikey)+make_bindings_type(filenames,color_input,colorkey,file_dictionary)+check_legend(legend)+"""\n</script>


</body>
</html>"""
	
	return block.replace('xxxxx',create_legend(legend[0],legend[1],legend[2]))

# get colors for just markers
def get_colors(color_input):
	colors=[['light green','#36db04'],
	['blue','#1717b5'],
	['red','#fb0026'],
	['yellow','#f9fb00'],
	['light blue','#00f4fb'],
	['orange','#dd5a21'],
	['purple','#6617b5'],
	['green','#1a7e55'],
	['brown','#b56617'],
	['pink','#F08080'],
	['default','#1766B5']]
	for row in colors:
		if row[0]==color_input:
			return row[1]
	return '#1766B5'

# get colors for everything else
def get_colors2(color_input):
	colors=[['light green','#36db04'],
	['blue','#1717b5'],
	['red','#fb0026'],
	['yellow','#f9fb00'],
	['light blue','#00f4fb'],
	['orange','#dd5a21'],
	['purple','#6617b5'],
	['green','#1a7e55'],
	['brown','#b56617'],
	['pink','#F08080'],
	['default','#1766B5']]
	for row in colors:
		if row[0]==color_input:
			return row[1]
	return '#1766B5'

# get colorline for marker
def get_colorline_marker(color_input):
	colorline="""				layer.setIcon(L.mapbox.marker.icon({'marker-color': '%s','marker-size': 'small'}))""" % get_colors(color_input)
	return colorline

# get colorline for non-marker objects
def get_colorline_marker2(color_input):
	colorline="""	    		layer.setStyle({color: '%s', weight: 3, opacity: 1});""" % get_colors2(color_input)
	return colorline

# THE FUNCTION YOU ACTUALLY USE WITH THIS MODULE
def loadparsehtml(filenames,apikey,**kwargs):
	color=''
	colorkey=''
	frame=False
	file_dictionary=False
	legend=['','','']



	for key,value in kwargs.iteritems():
		if key=='color':
			color=str(value)
		if key=='colorkey':
			colorkey=str(value)
		if key=='frame':
			if value==True:
				frame=True
		if key=='file_dictionary':
			file_dictionary=value
		if key=='legend':
			legend=value

	block=make_html(filenames,color,colorkey,apikey,file_dictionary,legend)
	if frame==True:
		with open('index.html','w') as f:
			f.write(block)
		f.close()
		return 'http://localhost:8000/index.html'
	else:
		load(block,'index.html')

# collection feature collecting all the geojson within the current directory
def collect():
	jsons=[]
	for dirpath, subdirs, files in os.walk(os.getcwd()):
	    for x in files:
	        if x.endswith(".geojson"):
	        	jsons.append(x)
	return jsons

def make_top():
	return '''<style>
.legend label,
.legend span {
  display:block;
  float:left;
  height:15px;
  width:20%;
  text-align:center;
  font-size:9px;
  color:#808080;
  }
</style>'''

def make_legend(title,colors,labels):
	colorhashs=[]
	for row in colors:
		colorhashs.append(get_colors(row))
	return '''
<div id='legend' style='display:none;'>
  <strong>%s</strong>
  <nav class='legend clearfix'>
    <span style='background:%s;'></span>
    <span style='background:%s;'></span>
    <span style='background:%s;'></span>
    <span style='background:%s;'></span>
    <span style='background:%s;'></span>
    <label>%s</label>
    <label>%s</label>
    <label>%s</label>
    <label>%s</label>
    <label>%s</label>
    <small>Source: <a href="https://github.com/murphy214/berrl">Made using Berrl</a></small>
</div>
''' % (title,colorhashs[0],colorhashs[1],colorhashs[2],colorhashs[3],colorhashs[4],labels[0],labels[1],labels[2],labels[3],labels[4])


def create_legend(title,colors,labels):
	if not title=='':
		return make_top()+'\n'+make_legend(title,colors,labels)
	else:
		return ''

def check_legend(legend):
	if legend[0]=='':
		return ''
	else:
		return 'var map2 = map.legendControl.addLegend(document.getElementById("legend").innerHTML);'



