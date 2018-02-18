from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import os
import requests
import json
import sys

from json import dumps
from bs4 import BeautifulSoup
#from lxml import html
import re
from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
	
	req = request.get_json(silent=True, force=True)
	result = req.get("result")
	parameters = result.get("parameters")
	companycode = parameters.get("companycode")
	companyname = parameters.get("companyname")
	
	if companyname is None:
		query = companycode

	else:
		companycode = getcompnaycode(companyname)
		if companycode is None:
			speech = "An error occurred while fetching the data!"
		else:
			speech = getstockquote(companycode,query)

	return responsedata(speech)

def responsedata(speech):
	returndata = {"speech": speech,"displayText": speech, "source": "stock-quote-by-anuj"}
	res = json.dumps(returndata, indent=4)
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r

def getcompnaycode(companyname):

        json_filename = "BSECodes.json"
        # reads it back
        with open(json_filename,"r") as f:
                data = f.read()
                # decoding the JSON to dictionay
                d = json.loads(data)
                query = companyname
        try:
                result = list([k for k in d if (companyname).lower() in k])
                #print ("Comapnies found " + str(len(result)))
                companycode = d[result[0]]['CompanyCode']
                query = result[0]
        except:
                return None

        return companycode

def getstockquote(companycode,query):
	try:
        # make an API request here
		url = 'https://www.bseindia.com/stock-share-price/SiteCache/EQHeaderData.aspx'
		params = {'text': companycode }
		page = requests.get(url, params)
		data = page.text
		
		url2 = "https://www.bseindia.com/stock-share-price/SiteCache/IrBackupStockReach.aspx"
		params2 = {'DebtFlag' : 'C', 'scripcode': companycode }
		page2 = requests.get(url2, params2)
		data2 = page2.text
		
		soup = BeautifulSoup(page2.content, 'html.parser')
		current_price = []

		for cell in soup.find_all('td'):
			current_price.append(cell.get_text('td'))
	

		data = re.sub('[^ 0-9,.|#:]', '', data)
		data = data.replace('##','|')
		#print (data)
		
		
		data = data.replace('#','|')
		data = data.replace(' ','')
		data = data.split('|')
		#print (data)
		
		price = data[5].split(",")
		del price[5]
		#messages = '[ { "platform" : "skype", "buttons":[ {"text": "Try Again", "postback":"again"} ] } ]'
		speech = "For " + str(query).upper() + \
				" Current Price is " + current_price[0] + \
				", and opening price was " + price[1] +\
				", with a high of " + price[2] + \
				", and low of " + price[3] + \
				". Previous closing price was " + current_price[0] +\
				". Price changed by " + current_price[3] +\
				", percentage change of " + current_price[4]

	except:
		speech = "An error occurred while fetching the data!"
		#messages = '[ { "platform" : "skype", "buttons":[ {"text": "Try Again", "postback":"again"} ] } ]'
		
	return speech




        
if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	print("Starting app on port %d" % port)

	app.run(debug=True, port=port, host='0.0.0.0')
