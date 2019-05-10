from django.shortcuts import render
from django.http import HttpResponse
from .models import OnionSites
import operator
import os
from django.db.models import Q
import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter
from django.utils.safestring import mark_safe
# Create your views here.

def index(request):
	onions = OnionSites.objects.all()
	context = {'onions':onions}
	return render(request,'onions/index.html',context)

def onionscanfiles(request,onionscanfile):
#	return HttpResponse(onionscanfile)
	return render(request,'onions/oniondata/'+onionscanfile)
"""
def results(request,keyword):
	datas = OnionSites.objects.filter(name = keyword )
	context = {'name':name, 'body':body}
	return render(request,'onions/result.html',context)
#	return render_to_response(request,'onions/result.html')
"""

def results(request):
	#onions = OnionSites.objects.all()

	keyword = request.GET.get('Keyword','')
	if keyword:
		q_objects = Q()
		q_objects.add(Q(body__icontains=keyword),Q.OR)
		q_objects.add(Q(name__icontains=keyword),Q.OR)
		
		onions = OnionSites.objects.filter(q_objects)
		context = {'onions':onions}
		return render(request,'onions/result.html',context)
	else:
		return render(request,'onions/index.html')


def data_prettified(data):
    """Function to display pretty version of our data"""
    # Convert the data to sorted, indented JSON
    response = json.dumps(data, sort_keys=True, indent=2)
    # Truncate the data. Alter as needed
    #response = response[:5000]
    # Get the Pygments formatter
    formatter = HtmlFormatter(style='colorful')
    # Highlight the data
    response = highlight(response, JsonLexer(), formatter)
    # Get the stylesheet
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    # Safe the output
    return mark_safe(style + response)

def datas(request,data):
	"""
				f = open(os.getcwd()+"\\datas\\"+data , 'rb')
				jd = f.read()	
				f.close()
				print(data_prettified(jd.decode()))
				return HttpResponse(data_prettified(jd.decode()))
				#return HttpResponse(json.dumps(jd.decode(), sort_keys=True, indent=4), content_type="application/json")
			"""
	json_string = None
	formatted_json = None
	with open(os.getcwd()+"\\datas\\"+data) as f:
		json_string = f.read()
	try:
	    parsed_json = json.loads(json_string)
	    formatted_json = json.dumps(parsed_json, indent = 4,sort_keys=True)
	    with open(os.getcwd()+"\\datas\\"+data,"w") as f:
	        f.write(formatted_json)
	except Exception as e:
	    print(repr(e))
	formatted_json = data_prettified(formatted_json)
	formatted_json = formatted_json.replace("\\n","<br>")
	formatted_json = formatted_json.replace("\\","")
	
	return HttpResponse(formatted_json)
