import os
import requests
import json

from json import dumps
from bs4 import BeautifulSoup
from lxml import html
import re
from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    
    req = request.get_json(silent=True, force=True)
    result = req.get("companycode")
    parameters = result.get("parameters")
    companycode = parameters.get("companycode")
    if companycode is None:
        return ("No company code!")

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
    table = soup.find('td', attrs={'class':'tbmainred'})
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

    json_string = '{ "Previous Close" : "' + price[0] + '",'
    json_string = json_string + '"Open" : "' + price[1] + '",'
    json_string = json_string + '"High" : "' + price[2] + '",'
    json_string = json_string + '"Low" : "' + price[3] + '",'
    json_string = json_string + '"Current" : "' + current_price + '"}'

    parsed_json = json.loads(json_string)
    
    speech = "Current Price is " + (parsed_json["Current"]) + \
            ", and opening price was " + (parsed_json["Open"]) +\
            ", with a high of " + (parsed_json["High"]) + \
            ", and low of " + (parsed_json["Low"]) + \
            ". Previous closing price was " + (parsed_json["Previous Close"])

    return {
            "speech": speech,
            "displayText": speech
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
