import csv
import pprint
import logging
import time
from logging.handlers import TimedRotatingFileHandler

from wallerexplorer.interrupt_test import open_ethlog
import requests
import json
from db_data.database import Process_data

logger = logging.getLogger("LOGETH")
logger.setLevel(logging.DEBUG)
ch = TimedRotatingFileHandler('ethlog', when="D", interval=1, backupCount=5, )
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(format)
logger.addHandler(ch)


def hex_dec(value):
    return (int(value, 16) / 10 ** 18)


def write_to_csv(name, data):
    with open("%s.csv" % name, mode='a', newline='')as f:
        # writer = csv.writer(f)
        # writer.writerow(args)
        f.write(data + '\n')


def counter(num):
    total = 0
    total = sum(total, num)
    return total


def getBlockByNumber(number):
    list = []
    url = 'http://192.168.3.31:8545'
    body = {"method": "eth_getBlockByNumber",
            "params": [str(hex(number)), True], "id": 1, "jsonrpc": "2.0"}
    r = requests.post(url=url, data=json.dumps(body), headers={
        "Content-Type": "application/json"})
    # result = r.json()['result']['hash']
    blockhash = r.json()['result']['hash']
    blockNumber = r.json()['result']['number']
    timestamp = r.json()['result']['timestamp']
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp, 16)))
    transactions = r.json()['result']['transactions']
    for transaction in transactions:
        from_add = transaction['from']
        to_add = transaction['to']
        if to_add == None:
            to_add = transaction['creates']
        transaction_hash = transaction['hash']
        value = transaction['value']  # 发送的以太数量，单位：wei
        gas = transaction['gas']  # Gas价格
        gasPrice = transaction['gasPrice']  # Gas使用量最大限额
        transactionIndex = transaction['transactionIndex']
        input_data = transaction['input']
        eth_transaction = (from_add, to_add, blockhash, int(blockNumber, 16), date,
                           int(gas, 16), int(gasPrice, 16), input_data, int(timestamp, 16),
                           int(transactionIndex, 16), transaction_hash, hex_dec(value))
        list.append(eth_transaction)

    return list


# getBlockByNumber()


def getTransactionByBlockHashAndIndex(hash, index=1):
    # 返回指定块内具有指定索引序号的交易。
    url = 'http://192.168.3.31:8545'
    body = {"method": "eth_getTransactionByBlockHashAndIndex",
            "params": [str(hash), str(hex(index))], "id": 1,
            "jsonrpc": "2.0"}
    r = requests.post(url=url, data=json.dumps(body), headers={
        "Content-Type": "application/json"})
    result = r.json()['result']['hash']
    # print(result)
    input = r.json()['result']['from']
    output = r.json()['result']['to']
    return result


# getTransactionByBlockHashAndIndex('0x1')


def getTransactionByHash(hash):
    url = 'http://192.168.3.31:8545'
    body = {"method": "eth_getTransactionByHash",
            "params": [str(hash)], "id": 1, "jsonrpc": "2.0"}
    r = requests.post(url=url, data=json.dumps(body), headers={
        "Content-Type": "application/json"})
    result = r.json()['result']
    # print(result)
    # hash  = r.json()['result']['hash']
    input = r.json()['result']['from']
    output = r.json()['result']['to']
    value = r.json()['result']['value']  # 发送的以太数量，单位：wei
    gas = r.json()['result']['gas']  # Gas价格
    gasPrice = r.json()['result']['gasPrice']  # Gas使用量最大限额
    blockHash = r.json()['result']['blockHash']
    blockNumber = r.json()['result']['blockNumber']
    transactionIndex = r.json()['result']['transactionIndex']
    input_data = r.json()['result']['input']
    # transaction = (hash + "," + input + "," + output + "," + value
    #                + "," + gas + "," + gasPrice)
    transaction = (hash, input, output, hex_dec(value), int(gas, 16), int(gasPrice, 16))
    print(hash)
    return transaction


# getTransactionByHash()

# for i in range(1100000, 1100010):
#     blockhash = getBlockByNumber(i)
#     # write_to_csv("块哈希", blockhash)
#     try:
#         j = 0
#         while True:
#             hash = getTransactionByBlockHashAndIndex(blockhash[0], j)
#             # write_to_csv('交易哈希', hash)
#             data = getTransactionByHash(hash)
#             # write_to_csv('交易详情', data)
#             data1 = (2, 3, 4, 5, 6, 7)
#             process_data.insert_eth_transation(*data)
#             j += 1
#     except:
#         continue
#     # , '交易哈希', '输入', '输出',
#     #                  '发送以太的数量', 'Gas价格', 'Gas使用量最大限额'
# print("总共耗时：", time.time() - start)

process_data = Process_data()


def eth_get_transaction(num=10700000, index=0):
    start = time.time()
    for i in range(num, 10700100):
        transaction_list = getBlockByNumber(i)
        print(i, end='\t')
        blocknumber = i
        try:
            blockhash = transaction_list[0][2]
        except:
            continue
        # j = 0
        print(index)
        for tran in transaction_list[index:]:
            process_data.insert_address(tran[0])
            process_data.insert_address(tran[1])
            process_data.insert_eth_transaction_new(*tran)
            # transaction_index = tran[-3]
            print(blocknumber,end='\t')
            j = transaction_list.index(tran)
            print(j)
            logger.debug(str(blocknumber) + " - " + str(j))
        index = 0
            # print(transaction_index)

        print('块高：' + str(blocknumber) + '\t' + '块哈希：' + blockhash + '\t' + "一共有交易：", end='')
        length = len(transaction_list)
        print(length)

    print("总共耗时：", time.time() - start)


if open_ethlog():
    num, index = open_ethlog()[0], open_ethlog()[1]
    eth_get_transaction(num, index+1)
if open_ethlog() == None:
    eth_get_transaction()
