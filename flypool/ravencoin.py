from requests import get
from json import loads, dump, dumps
from time import time,sleep
from os import system
import sys
import csv

from .utils import *


#constant
API = [
  'https://api-ravencoin.flypool.org/miner/{}/dashboard',
  'https://api-ravencoin.flypool.org/miner/{}/dashboard/payouts',
  'https://query1.finance.yahoo.com/v7/finance/quote?&symbols=RVN-USD&fields=regularMarketPrice',
  'https://api-ravencoin.flypool.org/miner/{}/settings',
  'https://api-ravencoin.flypool.org/miner/{}/worker/{}/history',
  'https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=1&symbol=FX:USDTWD:FOREX&quote=1'
]
TEMPLATE = ['''┌────────────────┬─────────────┐
│現在算力(60m)   │ {:<7} MH/s│
├────────────────┼─────────────┤
│平均算力(24h)   │ {:<7} MH/s│
├────────────────┼─────────────┤
├────────────────┼─────────────┤
│預測日收益      │ {:<7} RVN │
│                │ {:<7} NTD │
├────────────────┼─────────────┤
│距離下次出金    │ {:<7} hr  │
├────────────────┼─────────────┤
│出金數額下限    │ {:<7} RVN │
├────────────────┼─────────────┤
├────────────────┼─────────────┤
│Ravencoin價格   │ {:<7} NTD │
└────────────────┴─────────────┘''',
'''┌─────────┬────────────────────┐
│礦機名稱 │ {:<19}│
├─────────┴──────┬─────────────┤
│現在算力(10m)   │ {:<7} MH/s│
└────────────────┴─────────────┘'''
]


#get state from rvnermine
def get_miner_stat(id):
  #miner data
  data = loads(get(API[0].format(id)).content)['data']
  #payouts data
  pay = loads(get(API[1].format(id)).content)['data']
  #setting data
  setting = loads(get(API[3].format(id)).content)['data']

  # 1h = x rvn
  hash2pay = pay['estimates']['coinsPerMin']/pay['estimates']['averageHashrate']
  #all the hashrate data
  all_hashrate = [i['currentHashrate'] for i in data['statistics']]

  #average of 1 hour and 24 hour
  avg_1h = sum(all_hashrate[-6:])/6
  avg_24h = sum(all_hashrate)/144

  #unpaid balance
  unpaid = data['currentStatistics']['unpaid']
  #payout threshold
  threshold = setting['minPayout']

  duration = (threshold-unpaid)/1e8/(hash2pay*avg_24h)*60
  next_payout = threshold/1e8

  daily_profit = 1440*hash2pay*avg_24h

  return avg_1h, avg_24h, daily_profit, next_payout, duration, data['workers'], threshold/1e8

#get rvn price
def get_rvn_stat():
  price = float(loads(get(API[2]).content)["quoteResponse"]["result"][0]["regularMarketPrice"])
  u2n = float(loads(get(API[5]).content)["data"]["o"][0])
  return round(price*u2n,2)

#get all workers' status
def get_workers_his(id, workers):
  his = {}
  for i in workers:
    data = loads(get(API[4].format(id, i)).content)['data']
    his[i] = {i['time']:i['validShares'] for i in data}
  
  return his

#get and calc all the status
def get_stat(id, refresh=False, worker=False, log=False, path=None, lang=0, NTD=0):
  a6, a24, dp, np, du, wr, lim = get_miner_stat(id)
  price = get_rvn_stat()
  workers = get_workers_his(id, (i['worker'] for i in wr))

  a6, a24 = round(a6/1e6, 2),round(a24/1e6, 2)
  dp, np = round(dp,4), round(np, 4)

  if refresh:
    if sys.platform =='win32':
      system('cls')
    elif sys.platform == 'linux':
      system('cls')

  stat = TEMPLATE[0].format(
    a6,a24,
    round(dp,2), round(dp*price), 
    s2h(du), lim,
    price
  )
  if log:
    try:
      with open(path+'/log.json', 'r') as f:
        data = loads(f.read())
    except:
      data = {'workers':{i['worker']:0 for i in wr}}
    
    for name, his in workers.items():
      for time, shares in his.items():
        time_str = f'{t2d(time)}'
        now = eval(str(data.get(time_str, data['workers'])))
        now[name] = shares
        data[time_str] = now
    
    with open(path+'/log.json', 'w') as f:
      dump(data, f, indent=2)

  if worker:
    wrs = []
    for i in wr:
      wrs.append(TEMPLATE[1].format(
        i['worker'],
        round(i['currentHashrate']/1e6,2)
      ))
    print_block(stat,*wrs[:9])
    if len(wrs)>9:
      temp = []
      for i in range(9,len(wrs)):
        temp.append(wrs[i])
        if len(temp)==4:
          print_block(*temp)
          temp = []
      print_block(*temp)
  else:
    print(stat)

def json2csv(file, output):
  with open(file, 'r') as f:
    data = loads(f.read())
  table = dict2table(data)
  with open(output, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(table)


if __name__=='__main__':
  while True:
    get_stat('RUgySiBwfekLNhAS2bBz3hpwdBLnn82PGy', True, True)
    sleep(60)