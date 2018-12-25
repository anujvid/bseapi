import os
import json
import sys
from json import dumps
from bs4 import BeautifulSoup
#from lxml import html
import re
from flask import Flask
from flask import request
from flask import make_response
import requests



app = Flask(__name__)
##
##
@app.route('/webhook', methods=['POST'])

def webhook():
        
        req = request.get_json(silent=True, force=True)
        result = req.get("result")
        action = result.get("action")
        parameters = result.get("parameters")
        companycode = parameters.get("companycode")
        companyname = parameters.get("companyname")
        
        
        if companyname is None:
                query = companycode
        else:
                companycode = getcompnaycode(companyname)
                query = getcompnayname(companyname)

        companyname = getcompanydetails(companyname)
        query = companyname[0]
        companycode = companyname[2]

        speech = "No action taken!-" + action

        if action == 'getstockprice_byname':
                
                if companycode is None:
                        speech = "An error occurred while fetching the data!"
                else:
                        speech = getstockquote(companycode,query)

        if action == 'getstockprice':
                speech = getstockquote(companycode,query)

        if action == 'getperformance':
                speech = getperformance(companycode,query)

        if action == 'getbseindex':
                speech = getbseindex()


        return responsedata(speech)

def responsedata(speech):
        returndata = {"speech": speech,"displayText": speech, "source": "stock-quote-by-anuj"}
        res = json.dumps(returndata, indent=4)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r

def getcompanydetails(query):
        companycode_url ="https://api.bseindia.com/BseIndiaAPI/api/PeerSmartSearch/w"
        companycode_params = {'Type' : 'EQ', "text" : query }
        companycode_results = requests.get(companycode_url , companycode_params)
        soup = BeautifulSoup(companycode_results.content, 'html.parser')
        companyname = soup.find('a')
        companyname = companyname.span.text
        companydetails = companyname.split()

        return [companydetails[0], companydetails[2]]


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

def getcompnayname(companyname):

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

        return query

def getstockquote(companycode,query):
        try:
                Price_url = "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w"
                Price_params = {'scripcode': companycode, 'Debtflag' : '', 'seriesid': ''}
                Price_page = requests.get(Price_url , Price_params)
                Price_json = json.loads(Price_page.content)

                speech = "For " + Price_json['Cmpname']['FullN'] + \
                         " as on " + Price_json ['Header']['Ason'] +\
                         " Current Price is " + Price_json ['Header']['LTP'] + \
                         ", and opening price was " + Price_json ['Header']['Open'] +\
                         ", with a high of " + Price_json ['Header']['High'] + \
                         ", and low of " + Price_json ['Header']['Low'] + \
                         ". Previous closing price was " + Price_json ['Header']['PrevClose'] +\
                         ". Price changed by " + Price_json ['CurrRate']['Chg'] +\
                         ", percentage change of " + Price_json ['CurrRate']['PcChg']

        except:
                speech = "An error occurred while fetching the data!"
 
        return speech


def getperformance(companycode,query):

        try:

                results_url = "https://api.bseindia.com/BseIndiaAPI/api/TabResults/w"
                results_params = {'scripcode': companycode,'tabtype': 'RESULTS'}
                page_data2={}
                results_page = requests.get(url=results_url,params=results_params)
                page = json.loads(results_page.content)
                page_data2 = json.loads(page)
                x = 0
                speech = "For " + str(query).upper() + " Results for " + str(page_data2['col4']) + "\n"

                for list in page_data2:
                        speech = speech + str(page_data2['resultinCr'][x]['title']) + " is " + str(page_data2['resultinCr'][x]['v3']) + "\n"
                        x = x+1

                speech = speech + "Results for - " + str(page_data2['col2']) + "\n"
                
                x=0
                for list in page_data2:
                        speech = speech + str(page_data2['resultinCr'][x]['title']) + " is " + str(page_data2['resultinCr'][x]['v1']) + "\n"
                        x = x+1

                

        except:
                speech = "An error occurred while fetching the data!"

        return speech

def getbseindex():
    try:
        # make an API request here
        index_url = "https://api.bseindia.com/bseindia/api/Sensex/getSensexData"
        fields = str("{'fields': '2,3,4,5,6,7'}")
        index_params = {'json': fields }

        index_json2={}
        index_page = requests.get(url=index_url, params=index_params)
        index_json = str(json.loads(index_page.content))
        index_json = index_json.replace("[","")
        index_json = index_json.replace("]","")
        index_json = index_json.replace("'",'"')
        index_json2 = json.loads(index_json)
                
        speech = "As on " + index_json2['dttm'] + " current index is " + index_json2['ltp'] + " Change of " + index_json2['chg'] + " points and % of " +  index_json2['perchg'] 
    except:
        speech = "Sorry! unable to fetch data."
    return (speech)
    
        
if __name__ == '__main__':
        port = int(os.getenv('PORT', 5000))

        print("Starting app on port %d" % port)

        app.run(debug=True, port=port, host='0.0.0.0')
