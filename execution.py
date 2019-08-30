from base_fun import *

temp_list = sto_list()

for i in temp_list:
    try:
        stock_table(i)
    except:
        pass

mi_download()


date_Ashare()

median_result()

