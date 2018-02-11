from django.shortcuts import render
from django.http import HttpResponse
from .models import Greeting

# Create your views here.
@app.route('/home/<companycode>/<pricetype>')
def home(companycode,pricetype):
    # return HttpResponse('Hello from Python!')
    
    import requests
    import json

    
    from json import dumps
    from bs4 import BeautifulSoup
    from lxml import html
    import re
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
    return (parsed_json[pricetype])



def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

