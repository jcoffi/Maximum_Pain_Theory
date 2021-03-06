# About the code
#This code can be used to extract the option table of all the listed stocks on NSE.
#This will prepare the bar graphs suggesting max pain point.

import time
sta = time.clock()
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import re
import datetime

date = str(datetime.datetime.now()).split(' ')[0]
'''
try:
    Name = raw_input("Name of the stock ")
    Base_url =("https://www.nseindia.com/live_market/dynaContent/"+
           "live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol=" + Name+"&"+
           "symbol="+Name+"&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")
except:
    Base_url =("https://www.nseindia.com/live_market/dynaContent/"+
           "live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol=UBL&"+
           "symbol=UBL&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")

Name = "ubl"
Base_url =("https://www.nseindia.com/live_market/dynaContent/"+
           "live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol=UBL&"+
           "symbol=UBL&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")
'''
data_code = pd.read_excel("Code.xlsx")
S_LTP = []; MTP=[]; pcr = []; diff= [];Stk = [];Buy = []; Sell = []; Watch_out = []
dfmxc = [] ; dfmxp = []; conf = []; opr = []; comment = []

slp = 0
for Name in data_code['Code']:
    print (Name)


    #Name = raw_input("Name of the stock ")
    Base_url = "https://nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=797&symbol="+Name+"&symbol="+Name+"&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17"

    if Name is '':
        Base_url = "https://nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=797&symbol=pnb&symbol=pnb&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17"
        Name = 'pnb'

    page = requests.get(Base_url)
    page.status_code
    page.content

    for line in page:
        if Name in line:
            LTP = re.findall(">{} ([0-9.]+)".format(Name),line)
            try:
                LTP = float(LTP[0])
            except:
                continue
            print (Name,LTP)
            break

    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup.prettify())

    table_it = soup.find_all(class_="opttbldata")
    table_cls_1 = soup.find_all(id="octable")

    col_list = []

    # The code given below will pull the headers of the Option Chain table
    for mytable in table_cls_1:
        table_head = mytable.find('thead')

        try:
            rows = table_head.find_all('tr')
            for tr in rows:
                cols = tr.find_all('th')
                for th in cols:
                    er = th.text
                    ee = er.encode('utf8')
                    col_list.append(ee)

        except:
            print ("no thead")


    col_list_fnl = [e for e in col_list if e not in ('CALLS','PUTS','Chart','\xc2\xa0')]

    #print col_list_fnl                jetairways

    table_cls_2 = soup.find(id="octable")
    all_trs = table_cls_2.find_all('tr')
    req_row = table_cls_2.find_all('tr')

    new_table = pd.DataFrame(index=range(0,len(req_row)-3) , columns=col_list_fnl)

    row_marker = 0

    for row_number, tr_nos in enumerate(req_row):

         # This ensures that we use only the rows with values
         if row_number <=1 or row_number == len(req_row)-1:
             continue

         td_columns = tr_nos.find_all('td')

         # This removes the graphs columns
         select_cols = td_columns[1:22]
         cols_horizontal = range(0,len(select_cols))

         for nu, column in enumerate(select_cols):

             utf_string = column.get_text()
             utf_string = utf_string.strip('\n\r\t": ')
             tr = utf_string.encode('utf8')
             tr = tr.replace(',' , '')
             new_table.ix[row_marker,[nu]]= tr

         row_marker += 1

    #print new_table
    # fil = "/home/kvv/Dropbox/Stock Investment/Coding/Excel/{}.xlsx".format(Name)
    # fil =  "C:\\Users\\iitb_student\\Dropbox\\Stock_Investment\\Coding\\Analysis\\Excel\\{}.xlsx".format(Name)
#    fil = Name + 'Option_Chain_Table.xlsx'


    fil = os.getcwd()
    if "\\" in fil:
        fil = fil +  "\\Excel\\"
        if not os.path.exists(fil):
            os.makedirs(fil)
        fil = fil +  "{}.csv".format(Name)
    else:
        fil = fil +  "/Excel/"
        if not os.path.exists(fil):
            os.makedirs(fil)
        fil = fil +  "{}.csv".format(Name)

    new_table.to_csv(fil)
    newdata = pd.read_csv(fil)
    newdata = newdata.fillna(0)
    newdata = newdata.replace('-',0)
    try:
        newdata['Help'] = newdata['Strike Price'] - newdata['Strike Price'][0]
    except:
        continue
    newdata['CALL'] = pd.to_numeric(newdata['OI'])
    newdata['PUT'] = pd.to_numeric(newdata['OI.1'])

    a=1
    cumc = [0] ; cump= [0]
    nos = len(newdata['Strike Price'])
    while a < len(newdata['Strike Price']):
        temp = 0
        temp1 = 0
        for i in range(a):
            for j in range(a,a+1):
    #            print (i,j-i,newdata['CALL'][i] , newdata['Help'][j],a)
                temp = float(newdata['CALL'][i]) * newdata['Help'][j-i] + temp
                temp1 = float(newdata['PUT'][nos-i-1]) * newdata['Help'][j-i] + temp1
        cumc.append(temp)
        cump.append(temp1)
        a+=1

    newdata["CUM_Call"] = cumc
    newdata["CUM_Put"] = cump[::-1]
    newdata['TV'] = newdata["CUM_Call"]  + newdata["CUM_Put"]
    Exp = newdata[newdata["TV"] == min(newdata['TV'])]["Strike Price"].describe()[1]
    try:
	    PCR = sum(newdata['PUT'])/float(sum(newdata['CALL']))
    except:
    	PCR = 1
    gi = pd.Index(newdata['TV']).get_loc(min(newdata['TV']))
    try:
        int(gi)
    except:
        continue
    for i in range(gi-1,gi+1):
    #    print  # newdata['TV'][i]
    	try:
	        print int(newdata['Strike Price'][i]), round((newdata['TV'][i]-newdata['TV'][gi])/newdata['TV'][gi]*100,3)
    	except:
	        print ("Error")

    check = pd.DataFrame()
    check['Strike Price'] = newdata['Strike Price']
    check['Call'] = newdata['CALL']
    check['Put'] = newdata['PUT']
    check['CUM_Call'] = newdata['CUM_Call']
    check['CUM_Put'] = newdata['CUM_Put']
    check['TV'] = newdata['TV']
    S_LTP.append(LTP)
    MTP.append(Exp)
    pcr.append(PCR)
    temp2 = (Exp-LTP)/LTP*100
    diff.append(temp2)
    Stk.append(Name)

    fig, max_pain = plt.subplots()
    max_pain.bar(newdata['Strike Price'],newdata['TV'])
    plt.xticks(newdata['Strike Price'],rotation=90)
    try:
        title = "{}, 68 % chances {}; PCR {}; LTP {}; Diff {}".format(Name.upper(),Exp,round(PCR,1),LTP,round(temp2,1))
    except:
        title = "{}, 68 % chances {}; PCR {}; LTP {}".format(Name.upper(),Exp,round(PCR,1),LTP)

    plt.title(title)

    path = os.getcwd()
    if "\\" in path:
        path = path +  "\\Graphs\\"
        if not os.path.exists(path):
            os.makedirs(path)
        path = path +  "{}_{}.png".format(Name,date)
    else:
        path = path +  "/Graphs/"
        if not os.path.exists(path):
            os.makedirs(path)
        path = path +  "{}_{}.png".format(Name,date)


    plt.savefig(path)

    print ("There is 68 % chances that the stocks will expire at ",Exp)

    print ("PCR value",PCR)

    if PCR>1.3:
        print ("====================================================\n")
        print ("Bullish reversal might come in place",PCR,Name)
        print ("Stock might go up")
        print ("====================================================\n")

    elif PCR < 0.5:
        print ("====================================================\n")
        print ("Bearish reversal might kick off",PCR, Name)
        print ("Stock might go down")
        print ("====================================================\n")

    if PCR > 1.3:
        Buy.append((Name,PCR,Exp,LTP,diff))
    if PCR < 0.5 :
        Sell.append((Name,PCR,Exp,LTP,diff))

    if temp2 > 5 or temp2 <-5:
        Watch_out.append((Name,PCR,Exp,LTP,diff))
    try:
        MxP = newdata['Strike Price'][pd.Index(newdata['PUT']).get_loc(max(newdata['PUT']))]
        float(MxP)
    except:
        MxP = newdata['Strike Price'][pd.Index(newdata['PUT']).get_loc(max(newdata['PUT']))]
        MxP = MxP.describe()[3]
    try:
        MxC = newdata['Strike Price'][pd.Index(newdata['CALL']).get_loc(max(newdata['CALL']))]
        float(MxC)
    except:
        MxC = newdata['Strike Price'][pd.Index(newdata['CALL']).get_loc(max(newdata['CALL']))]
        MxC = MxC.describe()[7]

    print ("Max put is at {} strike price; OI: {}".format(MxP,max(newdata['PUT'])))
    print ("Max call is at {} strike price; OI: {}".format(MxC,max(newdata['CALL'])))

    print ("Range for the {} is {} to {}".format(Name,MxP,MxC))

    MxC1 = float(max(newdata['CALL']))
    MxP1 = float(max(newdata['PUT']))


    dfmxc.append(MxC)
    dfmxp.append(MxP)
    try:
	    conf.append((MxC1-MxP1)/MxP1*100)
    except:
    	conf.append(0)

    if LTP > MxC or LTP < MxP:
        print ("+++++++++BOOOOOMMMMMMMMMMMM+++++++++++++")
        try:
	        opr.append((Name,LTP,Exp,MxP,MxC,(MxC1-MxP1)/MxP1*100))
    	except:
    		opr.append((Name,LTP,Exp,MxP,MxC,0))
        pd.DataFrame(opr).to_excel("Fortune_{}.xlsx".format(date))
        comment.append(1)
    else:
        comment.append(0)
    slp+=1
    if slp%100==0:
        print ("+++++++++++++++++++  Resting a bit.......................")
        time.sleep(3)

fn = pd.DataFrame()

fn["Stock"] =    Stk
fn["PCR"] =    pcr
fn["LTP"] =    S_LTP
fn["MTP"] =    MTP
fn["Diff"] =    diff
fn["Lower"] =    dfmxp
fn["Upper"] =    dfmxc
fn["Confidence"] =    conf
fn["Comment"] = comment

fn.to_excel("Theory_{}.xlsx".format(date))

print ("Time taken {}".format(time.clock()-sta))
print "Fortune making companies found", sum(comment)

