import datetime,requests,re,os
import pandas as pd
import numpy as np

docu = os.getcwd() #创建数据保存文件夹
global doc_path
doc_path = ['database','database\\raw','database\\date_Ashare','database\\market_index']
for item in doc_path:
    isExists=os.path.exists(item)
    if not isExists:
        os.makedirs(item)

#指数
market_index = [['0000001','上证指数'],['0000300','沪深300'],['1399001','深证成指'],['1399005','中小板指'],['1399006','创业板指']]

endTime = datetime.datetime.now() #时间设定

delta = datetime.timedelta(days=-1000)
startTime = endTime + delta

endTime = endTime.strftime('%Y%m%d')
startTime = startTime.strftime('%Y%m%d')

def stock_table(stockCode):
    if (len(re.findall('^60[0-9]{4}', stockCode)) > 0):
        stRenew = '0' + stockCode
    else:
        stRenew = '1' + stockCode

    endTime = datetime.datetime.now()

    delta = datetime.timedelta(days=-1000)
    startTime = endTime + delta

    endTime = endTime.strftime('%Y%m%d')
    startTime = startTime.strftime('%Y%m%d')

    url = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP' % ( stRenew, startTime, endTime)

    data_raw = requests.get(url).text
    if len(data_raw)>1024:
        with open('database\\raw\\%s.csv'%stockCode, 'w', encoding='gbk') as f:
            f.write(data_raw)
    else:
        print(stockCode +"     "+ len(data_raw))


def sto_list():
    url = 'http://quote.eastmoney.com/stock_list.html'

    sto_list = requests.get(url)

    sto_list.encoding = 'gb2312'

    sto_list = sto_list.text

    with open('body.txt', 'w', encoding='utf8') as f:
        f.write(sto_list)

    sto_list = re.findall('<li>.*?">.*?\(([306][0-9]{5})\)</a></li>', sto_list)
    return(sto_list)

def stock_renew(stockCode): #更新使用
    filename = 'database\\raw\\%s.csv' % stockCode

    temp = pd.read_csv(filename)  # [:,1:]
    temp.drop(temp.columns[0], axis=1, inplace=True)

    temp_date = temp[1:2]['日期'][1]

    if (len(re.findall('^60[0-9]{4}', stockCode)) > 0):
        stRenew = '0' + stockCode
    else:
        stRenew = '1' + stockCode

    endTime = datetime.datetime.now()

    delta = datetime.timedelta(days=-1000)
    startTime = endTime + delta

    endTime = endTime.strftime('%Y%m%d')
    startTime = startTime.strftime('%Y%m%d')

    url = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP' % (
    stRenew, startTime, endTime)

    data_raw = requests.get(url).text

    with open('temp.csv', 'w', encoding='utf8') as f:
        f.write(data_raw)

    newest = pd.read_csv('temp.csv')

    date_index = newest.set_index('日期')

    for index_final, stock_date in enumerate(newest['日期']):
        if stock_date == temp_date:
            break

    temp_insert = newest[0:index_final - 1]


def mi_download():
    result = []
    for index,item in enumerate(market_index):
        url = 'http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP' % (item[0], startTime, endTime)
        data_raw = requests.get(url).text
        with open('database/market_index/%s.csv'%item[1],'w', encoding='gbk') as f:
            f.write(data_raw)
        data_raw = pd.read_csv('database/market_index/%s.csv'%item[1],encoding="gbk")
        result= result +[market_index[index] + [data_raw]]
    return result
    
    
temp_mi = mi_download()#读指数文件

def date_Ashare():# 计算每日中位数
    stock_files = os.listdir(doc_path[1]) #读股票文件
    ssei = temp_mi[1][2]
    ssei_colname = ssei.columns.tolist()
    stockdates = ssei['日期'].tolist()

    median_files = os.listdir(doc_path[2])
    for s_date in stockdates:
        print(s_date)
        temp_name = s_date+'.csv'
        if temp_name not in median_files:
            result = pd.DataFrame()
            for item in temp_mi:
                temp = item[2]
                stock_value = temp[temp.日期 == s_date]
                result = result.append(stock_value, sort=False)
            for item in stock_files:
                try:
                    temp = pd.read_csv(doc_path[1]+'\\' + item,encoding="gbk")
                    stock_value = temp[temp.日期 == s_date]
                    result = result.append(stock_value, sort=False)
                except:
                    pass
            result.to_csv(doc_path[2] + '\\'+s_date + '.csv', sep=',', index=None, encoding="utf_8_sig")
    

def median_result():
    files = os.listdir(doc_path[2])

    median_general = pd.DataFrame()

    for item in files:
        temp_date = re.sub('.csv', '', item)
        temp = pd.read_csv('%s\\%s'%(doc_path[2],item))
        temp_day = temp['涨跌幅'].tolist()
        temp_index = temp_day[0:5]
        temp_day = temp_day[5:]
        temp_day = list(filter(lambda x: x != 'None', temp_day))
        temp_day = [float(x) for x in temp_day]
        temp_median = np.median(temp_day)

        result = pd.DataFrame([temp_date]+temp_index+[temp_median]).T
        median_general = median_general.append(result)
    median_general.columns = ['日期', '上证涨跌','沪深300涨跌','深证涨跌','中小板指涨跌', '创业板指涨跌','当日中位']
    median_general.to_csv('每日中位数.csv', sep=',', index=None, encoding="utf_8_sig")
