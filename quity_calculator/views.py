from django.shortcuts import render
from django.http import HttpResponse
import json,requests
import datetime as dt
# Create your views here.

def index(request):
    return render(request,'home.html',{})

def get_equity_data_init(request):
    response = requests.get("http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=53&tp=1&frmdt=01-Apr-2015")
    converted_data = convert_into_json(response.content)
    return HttpResponse(
        json.dumps(converted_data),
        content_type='application/json',
        status=200
    )

def convert_into_json(data):
    newline_seperated_data = data.decode("utf-8").split('\r\n')
    data_list=list()
    for element in newline_seperated_data:
        if ';' in element:
            colon_seperated_data = element.split(';')
            new_data = dict()
            new_data['scheme_code'] = colon_seperated_data[0]
            new_data['scheme_name'] = colon_seperated_data[1]
            new_data['ISIN Div Payout/ISIN Growth'] = colon_seperated_data[2]
            new_data['ISIN Div Reinvestment'] = colon_seperated_data[3]
            new_data['Net Asset Value'] = colon_seperated_data[4]
            new_data['Repurchase Price'] = colon_seperated_data[5]
            new_data['Sale Price'] = colon_seperated_data[6]
            new_data['Date'] = colon_seperated_data[7]
            data_list.append(new_data)
    return data_list

def get_todays_value(request):
    date = '01-Apr-2015'
    if request.POST.get('frmdt') not in(None,'null','Null',0,'') :
        requested_date = dt.datetime.strptime(request.POST.get('frmdt'),'%Y-%m-%d')
        now = dt.datetime.now()
        requested_datetime = dt.datetime.combine(requested_date,now.time())
        if now > requested_datetime and requested_datetime > dt.datetime (2015, 1, 1,0,0,0):
            date = dt.datetime.strftime(requested_date,'%d-%b-%Y')
    scheme_id = request.POST.get('scheme_id')
    amount_invested = 0
    if request.POST.get('amount_invested') not in(None,'null','Null','') :
        amount_invested = float(request.POST.get('amount_invested'))
    response = requests.get("http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=53&tp=1&frmdt={}".format(date))
    converted_data = convert_into_json(response.content)
    stack = 0.0 
    price_today = 0.0
    for single_element in converted_data:
        if 'scheme_code' in single_element and single_element['scheme_code'] == scheme_id :
            selected_scheme = single_element
            stack = float(amount_invested)/float(selected_scheme['Net Asset Value'])
            break
    
    flag=False
    today = dt.date.today()
    while flag == False:
        yesterday = today - dt.timedelta(1) 
        fromdate = dt.datetime.strftime( yesterday,'%d-%b-%Y')
        response = requests.get("http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=53&tp=1&frmdt={}".format(fromdate))
        converted_data = convert_into_json(response.content)
        for single_element in converted_data:
            if 'scheme_code' in single_element and single_element['scheme_code'] == scheme_id :
                selected_scheme = single_element
                print(selected_scheme['Net Asset Value'])
                price_today = float(selected_scheme['Net Asset Value']) * stack
                flag= True
                break
        today = yesterday
    calculated_response = list()
    calculated_response.append({'stack_bought': stack,'price_today': price_today})
    return HttpResponse(
        json.dumps(calculated_response),
        content_type='application/json',
        status=200
    )