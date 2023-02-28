from pprint import pprint
import openpyxl
import pandas as pd
import json
import grequests
import warnings
warnings.simplefilter("ignore")

street = 'Сумской'
house = 17
building = 2

#headers, чтобы не вылезала ошибка
headers = {'Accept': '*/*',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

sites = []
#заполняем список сайтс, ссылками на каждую комнату
for i in range(1, 600):
    url = f"https://rosreestr.gov.ru/api/online/address/fir_objects?macroRegionId=145000000000&RegionId=145296000000&street={street}&building={building}&house={house}&apartment={i}" #building={building}&
    sites.append(url)
#print(sites)

#get запросы с помощью grequests по всем url в sites
requests = (grequests.get(url, headers=headers, verify=False) for url in sites)

#получаем список responses, если статус код не устраивает, тогда ошибка
try:
    responses = grequests.map(requests)
    for response in responses:
        if response.status_code != 200:
            response.raise_for_status()
except Exception as e:
    print(f"Error: {e}")
#иначе цикл по всем ответам в responses, забираем содержимое в формате json и добавляем в массив dataFrame'ов
else:
    dfs = []
    for i in responses:
        try:
            content = json.loads(i.content.decode())
            dfs.append(pd.DataFrame(content))
        except json.JSONDecodeError:
            print(f"Error: JSONDecodeError for {i.url}")
    #объединяем полученный массив в один дата фрейм
    df = pd.concat(dfs, ignore_index=True, sort=False)

    #Сортировка по квартирам (если нужна)
    #df = df.sort_values(by='apartment', key=lambda x: x.str.split(',| |-').str[0].astype(int),   ascending=True)

    #Дописываю номера квартир в адрес, там где они не прописаны
    #for i in range(0, len(df)):
    #    if df["addressNotes"][i].find(df["apartment"][i]) < 0:
    #        df["addressNotes"][i]=df["addressNotes"][i] + ", кв. " + str(df["apartment"][i])

    #оставляю только нужные мне столбцы
    kad = df[["addressNotes", "objectCn"]]
    #Убираю дупликаты по столбцы кадастровых номеров
    kad = kad.drop_duplicates(subset=['objectCn'])
    #убираем строки с пустыми кадастровыми номерами
    kad = kad.dropna(subset=['objectCn'])
    #Переводим в excel полную таблицу и таблицу с только нужными столбцами
    df.to_excel('pandas_to_excel_no_index_header.xlsx', index=False, header=df.columns)
    kad.to_excel('kad_adr__no_index_header.xlsx', index=False, header=kad.columns)

    print(kad)



