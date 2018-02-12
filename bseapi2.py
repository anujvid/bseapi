from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

import os
import requests
import json

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
    
    if companycode is None:
        return ("No company code!")

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
	    #try:
	    soup = BeautifulSoup(page2.content, 'html.parser')
	    table = soup.find('td')
	    current_price = str(table.text)
    #except AttributeError:
    #	current_price = "Not Found!"
    #print (current_price)
    
    
	    data = re.sub('[^ 0-9,.|#:]', '', data)
	    data = data.replace('##','|')
	    #print (data)
	    
	    
	    data = data.replace('#','|')
	    data = data.replace(' ','')
	    data = data.split('|')
	    #print (data)
	    
	    price = data[5].split(",")
	    del price[5]
	    
	    speech = "Current Price is " + current_price + \
	            ", and opening price was " + price[1] +\
	            ", with a high of " + price[2] + \
	            ", and low of " + price[3] + \
	            ". Previous closing price was " + price[0]
	 except:
	 	speech = "An error occurred while fetching the data! Please try later"


    returndata = {"speech": speech,"displayText": speech, "source": "stock-quote-by-anuj"}
    res = json.dumps(returndata, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
