from general.general_constants import *
from db import blockchain_database

from web3 import Web3
import requests

import json

from datetime import datetime
import time
import calendar

import math


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CUSTOM EXCEPTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class GetNodeLatestIndexError(Exception):
    pass

class GetNodeArchivalIndexError(Exception):
    pass

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getNode
# **kwargs:
# 'block' = 'latest' -> retrieves a Full Node / 'block' = block or not passed onto the function -> retrieves an Archival Node
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getNode(blockchain, **kwargs):
    
    if blockchain == ETHEREUM:
        node = NODE_ETH

    elif blockchain == POLYGON:
        node = NODE_POL

    elif blockchain == XDAI:
        node = NODE_XDAI

    elif blockchain == BINANCE:
        node = NODE_BINANCE

    elif blockchain == AVALANCHE:
        node = NODE_AVALANCHE

    elif blockchain == FANTOM:
        node = NODE_FANTOM

    elif blockchain == ROPSTEN:
        node = NODE_ROPSTEN

    elif blockchain == KOVAN:
        node = NODE_KOVAN

    elif blockchain == GOERLI:
        node = NODE_GOERLI

    try:
        block = kwargs['block']
    except:
        block = 'latest'

    try:
        index = kwargs['index']
    except:
        index = 0

    if block == 'latest':
        if index > (len(node['latest']) - 1):
            raise GetNodeLatestIndexError
        else:
             web3 = Web3(Web3.HTTPProvider(node['latest'][index]))

    else:
        if index > (len(node['archival']) - 1):
            raise GetNodeArchivalIndexError
        else:
            web3 = Web3(Web3.HTTPProvider(node['archival'][index]))

    return web3 

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPriceZapper - Test
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPriceZapper():
    
    data = requests.get('https://api.zapper.fi/v2/prices/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48?network=ethereum&timeFrame=hour&currency=USD&api_key=04a45cb5-16d6-4d28-9ccc-e68ed47270f3').json()['prices']
    print(data)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPriceCoinGecko
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPriceCoinGecko(token_address, timestamp, blockchain):
    
    if blockchain != ETHEREUM and blockchain != XDAI and blockchain != POLYGON:
        return [timestamp, None]

    if token_address == ZERO_ADDRESS:
        if blockchain == POLYGON:
            coin_id = 'matic-network'
        else:
            coin_id = blockchain

        data = requests.get(API_COINGECKO_COINID_PRICE_RANGE % (coin_id, timestamp - 3600 * 23, timestamp + 3600 * 1))
        if data.status_code != 200:
            return [data.status_code, [timestamp, None]]
        else:
            data = data.json()['prices']
            if data == []:
                data = requests.get(API_COINGECKO_COINID_PRICE_RANGE % (
                coin_id, timestamp - 3600 * 24 * 40, timestamp + 3600 * 24 * 40))
                if data.status_code != 200:
                    return [data.status_code, [timestamp, None]]
                else:
                    data = data.json()['prices']
                    if data == []:
                        data = requests.get(API_COINGECKO_COINID_PRICE_RANGE % (
                        coin_id, timestamp - 3600 * 24 * 180, timestamp + 3600 * 24 * 180))
                        if data.status_code != 200:
                            return [data.status_code, [timestamp, None]]
                        else:
                            data = data.json()['prices']

    else:
        if blockchain == POLYGON:
            blockchain_id = 'polygon-pos'
        else:
            blockchain_id = blockchain

        data = requests.get(API_COINGECKO_BLOCKCHAINID_TOKENADDRESS_PRICE_RANGE % (
        blockchain_id, token_address, timestamp - 3600 * 23, timestamp + 3600 * 1))
        if data.status_code != 200:
            return [data.status_code, [timestamp, None]]
        else:
            data = data.json()['prices']
            if data == []:
                data = requests.get(API_COINGECKO_BLOCKCHAINID_TOKENADDRESS_PRICE_RANGE % (
                blockchain_id, token_address, timestamp - 3600 * 24 * 40, timestamp + 3600 * 24 * 40))
                if data.status_code != 200:
                    return [data.status_code, [timestamp, None]]
                else:
                    data = data.json()['prices']
                    if data == []:
                        data = requests.get(API_COINGECKO_BLOCKCHAINID_TOKENADDRESS_PRICE_RANGE % (
                        blockchain_id, token_address, timestamp - 3600 * 24 * 180, timestamp + 3600 * 24 * 180))
                        if data.status_code != 200:
                            return [data.status_code, [timestamp, None]]
                        else:
                            data = data.json()['prices']

    if data == [] or data == None:
        return [200, [timestamp, None]]
    else:
        if len(data) == 1:
            return [200,[math.floor(data[0][0] / 1000),data[0][1]]]
        i = 0
        while int(data[i][0]) < timestamp * 1000:
            i += 1
            if i == len(data):
                break

        if i == len(data):
            return [200, [math.floor(data[i - 1][0] / 1000), data[i - 1][1]]]
        else:
            return [200, [timestamp, (
                        (timestamp * 1000 - data[i - 1][0]) * data[i][1] + (data[i][0] - timestamp * 1000) *
                        data[i - 1][1]) / (data[i][0] - data[i - 1][0])]]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# lastBlock
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'block' = block identifier used to call the getNode() function
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def lastBlock(blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            block = kwargs['block']
        except:
            block = 'latest'

        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    return web3.eth.blockNumber

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# timestampToDate
# **kwargs:
# 'utc' = timezone of the Output is UTC(+'utc')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def timestampToDate(timestamp, **kwargs):
    
    try:
        utc = kwargs['utc']
    except:
        utc = 0

    return datetime.utcfromtimestamp(timestamp + 3600 * utc).strftime('%Y-%m-%d %H:%M:%S')

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# timestampToBlock
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def timestampToBlock(timestamp, blockchain):
    
    data = None

    while data is None:
        if blockchain == ETHEREUM:
            data = requests.get(API_ETHERSCAN_GETBLOCKNOBYTIME % (timestamp, API_KEY_ETHERSCAN)).json()['result']

        elif blockchain == POLYGON:
            data = requests.get(API_POLYGONSCAN_GETBLOCKNOBYTIME % (timestamp, API_KEY_POLSCAN)).json()['result']

        elif blockchain == XDAI:
            data = requests.get(API_BLOCKSCOUT_GETBLOCKNOBYTIME % timestamp).json()['result']

            if data is None:
                time.sleep(0.1)
            else:
                data = data['blockNumber']

        elif blockchain == BINANCE:
            data = requests.get(API_BINANCE_GETBLOCKNOBYTIME % (timestamp, API_KEY_BINANCE)).json()['result']

        elif blockchain == AVALANCHE:
            data = requests.get(API_AVALANCHE_GETBLOCKNOBYTIME % (timestamp, API_KEY_AVALANCHE)).json()['result']

        elif blockchain == FANTOM:
            data = requests.get(API_FANTOM_GETBLOCKNOBYTIME % (timestamp, API_KEY_FANTOM)).json()['result']

        elif blockchain == ROPSTEN:
            data = requests.get(API_ROPSTEN_GETBLOCKNOBYTIME % (timestamp, API_KEY_ETHERSCAN), headers = TESTNET_HEADER).json()['result']

        elif blockchain == KOVAN:
            data = requests.get(API_KOVAN_GETBLOCKNOBYTIME % (timestamp, API_KEY_ETHERSCAN), headers = TESTNET_HEADER).json()['result']

        elif blockchain == GOERLI:
            data = requests.get(API_GOERLI_GETBLOCKNOBYTIME % (timestamp, API_KEY_ETHERSCAN), headers = TESTNET_HEADER).json()['result']

    return int(data)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# dateToTimestamp
# **kwargs:
# 'utc' = timezone of the Input is UTC(+'utc')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def dateToTimestamp(datestring, **kwargs):
    
    try:
        utc = kwargs['utc']
    except:
        utc = 0

    #   localTimestamp = math.floor(time.mktime(datetime.strptime(datestring,'%Y-%m-%d %H:%M:%S').timetuple()) + 3600 * utc)
    utc_timestamp = math.floor(
        calendar.timegm(datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S').timetuple()) - 3600 * utc)

    return utc_timestamp

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# dateToBlock
# **kwargs:
# 'utc' = timezone of the Output is UTC(+'utc')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def dateToBlock(datestring, blockchain, **kwargs):
    
    try:
        utc = kwargs['utc']
    except:
        utc = 0

    return timestampToBlock(dateToTimestamp(datestring, utc = utc), blockchain)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# blockToTimestamp
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def blockToTimestamp(block, blockchain):
    
    data = None

    while data is None:
        if blockchain == ETHEREUM:
            data = requests.get(API_ETHERSCAN_GETBLOCKREWARD % (block, API_KEY_ETHERSCAN)).json()['result']['timeStamp']

        elif blockchain == POLYGON:
            data = requests.get(API_POLYGONSCAN_GETBLOCKREWARD % (block, API_KEY_POLSCAN)).json()['result']['timeStamp']

        elif blockchain == XDAI:
            data = requests.get(API_BLOCKSCOUT_GETBLOCKREWARD % block).json()['result']['timeStamp']

        elif blockchain == BINANCE:
            data = requests.get(API_BINANCE_GETBLOCKREWARD % (block, API_KEY_BINANCE)).json()['result']['timeStamp']

        elif blockchain == ROPSTEN:
            data = requests.get(API_ROPSTEN_GETBLOCKREWARD % (block, API_KEY_ETHERSCAN), headers=TESTNET_HEADER).json()['result']['timeStamp']

        elif blockchain == KOVAN:
            data = requests.get(API_KOVAN_GETBLOCKREWARD % (block, API_KEY_ETHERSCAN), headers=TESTNET_HEADER).json()['result']['timeStamp']

        elif blockchain == GOERLI:
            data = requests.get(API_GOERLI_GETBLOCKREWARD % (block, API_KEY_ETHERSCAN), headers=TESTNET_HEADER).json()['result']['timeStamp']

    return int(data)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# blockToDate
# **kwargs:
# 'utc' = timezone of the Output is UTC(+'utc')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def blockToDate(block, blockchain, **kwargs):
    
    try:
        utc = kwargs['utc']
    except:
        utc = 0

    return timestampToDate(blockToTimestamp(block, blockchain), utc = utc)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ERC20 TOKENS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# tokenInfo
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def tokenInfo(token_address, blockchain):  # NO ESTÁ POLYGON

    if blockchain.lower() == ETHEREUM:
        data = requests.get(API_ETHPLORER_GETTOKENINFO % (token_address, API_KEY_ETHPLORER)).json()

    elif blockchain.lower() == XDAI:
        data = requests.get(API_BLOCKSCOUT_GETTOKENCONTRACT % token_address).json()['result']

    return data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# balanceOf
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'decimals' = specifies the number of decimals used to calculate the balance
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def balanceOf(address, contract_address, block, blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    try:
        decimals = kwargs['decimals']
    except:
        decimals = 0

    if contract_address == ZERO_ADDRESS:
        return web3.eth.get_balance(address, block) / (10 ** 18)

    else:
        token_contract = web3.eth.contract(address = web3.toChecksumAddress(contract_address), abi = json.loads(ABI_TOKEN_SIMPLIFIED))
        
        if decimals == 0:
            decimals = token_contract.functions.decimals().call()

        try:
            balance = token_contract.functions.balanceOf(address).call(block_identifier = block)
        except:
            balance = 0

        return balance / (10 ** decimals)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# totalSupply
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def totalSupply(token_address, block, blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    token_contract = web3.eth.contract(address=web3.toChecksumAddress(token_address), abi = json.loads(ABI_TOKEN_SIMPLIFIED))
    total_supply = token_contract.functions.totalSupply().call(block_identifier = block)
    decimals = token_contract.functions.decimals().call(block_identifier = block)

    return total_supply / (10 ** decimals)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getDecimals
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'block' = block identifier used to call the getNode() function
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getDecimals(token_address, blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            block = kwargs['block']
        except:
            block = 'latest'

        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    if token_address == ZERO_ADDRESS:
        decimals = 18
    else:
        token_contract = web3.eth.contract(address = web3.toChecksumAddress(token_address), abi = json.loads(ABI_TOKEN_SIMPLIFIED))
        decimals = token_contract.functions.decimals().call()

    return decimals

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getSymbol
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'block' = block identifier used to call the getNode() function
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getSymbol(token_address, blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            block = kwargs['block']
        except:
            block = 'latest'

        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    if token_address == ZERO_ADDRESS:
        if blockchain == ETHEREUM:
            symbol = 'ETH'
        elif blockchain == POLYGON:
            symbol = 'MATIC'
        elif blockchain == XDAI:
            symbol = 'XDAI'
    else:
        token_contract = web3.eth.contract(address = web3.toChecksumAddress(token_address), abi = ABI_TOKEN_SIMPLIFIED)
        symbol = token_contract.functions.symbol().call()

    return symbol


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CONTRACTS AND ABIS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getContractABI
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getContractABI(contract_address, blockchain):
   
    data = None

    while data is None:
        if blockchain == ETHEREUM:
            data = requests.get(API_ETHERSCAN_GETABI % (contract_address, API_KEY_ETHERSCAN)).json()['result']

        elif blockchain == POLYGON:
            data = requests.get(API_POLYGONSCAN_GETABI % (contract_address, API_KEY_POLSCAN)).json()['result']

        elif blockchain == XDAI:
            data = requests.get(API_BLOCKSCOUT_GETABI % contract_address).json()['result']

        elif blockchain == BINANCE:
            data = requests.get(API_BINANCE_GETABI % (contract_address, API_KEY_BINANCE)).json()['result']

        elif blockchain == ROPSTEN:
            data = requests.get(API_ROPSTEN_GETABI % (contract_address, API_KEY_ETHERSCAN), headers = TESTNET_HEADER).json()['result']

        elif blockchain == KOVAN:
            data = requests.get(API_KOVAN_GETABI % (contract_address, API_KEY_ETHERSCAN), headers = TESTNET_HEADER).json()['result']

        elif blockchain == GOERLI:
            data = requests.get(API_GOERLI_GETABI % (contract_address, API_KEY_ETHERSCAN), headers = TESTNET_HEADER).json()['result']

    return data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getContract
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'block' = block identifier used to call the getNode() function
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getContract(contract_address, blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            block = kwargs['block']
        except:
            block = 'latest'

        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    try:
        abi = kwargs['abi']
    except:
        abi = getContractABI(contract_address, blockchain)

    if not web3.isChecksumAddress(contract_address):
        contract_address = web3.toChecksumAddress(contract_address)

    return web3.eth.contract(address = contract_address, abi = abi)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getContractProxyABI
# **kwargs:
# 'web3' = web3 (Node) -> Improves performance
# 'block' = block identifier used to call the getNode() function
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getContractProxyABI(contract_address, abi_contract_address, blockchain, **kwargs):
    
    try:
        web3 = kwargs['web3']
    except:
        try:
            block = kwargs['block']
        except:
            block = 'latest'

        try:
            index = kwargs['index']
        except:
            index = 0

        web3 = getNode(blockchain, block = block, index = index)

    address = web3.toChecksumAddress(contract_address)

    return web3.eth.contract(address = address, abi = getContractABI(abi_contract_address, blockchain))


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ACCOUNTS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getTokenTx
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getTokenTx(token_address, contract_address, block_start, block_end, blockchain):
   
    data = None

    if blockchain == ETHEREUM:
        data = requests.get(API_ETHERSCAN_TOKENTX % (token_address, contract_address, block_start, block_end, API_KEY_ETHERSCAN)).json()['result']

    elif blockchain == POLYGON:
        data = requests.get(API_POLYGONSCAN_TOKENTX % (token_address, contract_address, block_start, block_end, API_KEY_POLSCAN)).json()['result']

    elif blockchain == XDAI:
        data = requests.get(API_BLOCKSCOUT_TOKENTX % (token_address, contract_address, block_start, block_end)).json()['result']

    return data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getTxList
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getTxList(contract_address, block_start, block_end, blockchain):
   
    data = None

    if blockchain == ETHEREUM:
        data = requests.get(API_ETHERSCAN_TXLIST % (contract_address, block_start, block_end, API_KEY_ETHERSCAN)).json()['result']

    elif blockchain == POLYGON:
        data = requests.get(API_POLYGONSCAN_TXLIST % (contract_address, block_start, block_end, API_KEY_POLSCAN)).json()['result']

    elif blockchain == XDAI:
        data = requests.get(API_BLOCKSCOUT_TXLIST % (contract_address, block_start, block_end)).json()['result']

    return data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LOGS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLogs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLogs(block_start, block_end, address, topic0, blockchain, **kwargs):

    data = None
    optional_parameters = ''

    for key, value in kwargs.items():

        if key == 'topic1':
            if value:
                optional_parameters += '&topic1=%s' % (value)
                continue
        
        if key == 'topic2':
            if value:
                optional_parameters += '&topic2=%s' % (value)
                continue

        if key == 'topic3':
            if value:
                optional_parameters += '&topic3=%s' % (value)
                continue
        
        if key == 'topic0_1_opr':
            if value:
                optional_parameters += '&topic0_1_opr=%s' % (value)
                continue
        
        if key == 'topic0_2_opr':
            if value:
                optional_parameters += '&topic0_2_opr=%s' % (value)
                continue
        
        if key == 'topic0_3_opr':
            if value:
                optional_parameters += '&topic0_3_opr=%s' % (value)
                continue
        
        if key == 'topic1_2_opr':
            if value:
                optional_parameters += '&topic1_2_opr=%s' % (value) 
                continue
        
        if key == 'topic1_3_opr':
            if value:
                optional_parameters += '&topic1_3_opr=%s' % (value)
                continue
        
        if key == 'topic2_3_opr':
            if value:
                optional_parameters += '&topic2_3_opr=%s' % (value)
                continue

    
    if blockchain == ETHEREUM:
        data = requests.get(API_ETHERSCAN_GETLOGS % (block_start, block_end, address, topic0, API_KEY_ETHERSCAN) + optional_parameters).json()['result']

    elif blockchain == POLYGON:
        data = requests.get(API_POLYGONSCAN_GETLOGS % (block_start, block_end, address, topic0, API_KEY_POLSCAN) + optional_parameters).json()['result']

    elif blockchain == XDAI:
        data = requests.get(API_BLOCKSCOUT_GETLOGS % (block_start, block_end, address, topic0) + optional_parameters).json()['result']

    return data



LPTOKENSDATABASE = blockchain_database.LPTOKENSDATABASE

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# liquidity tokens and pools

def LPtokenUnderlying(lptoken_address, amount, block, blockchain):
    
    web3 = getNode(blockchain, block=block)
    index = [LPTOKENSDATABASE[i][1].lower() for i in range(len(LPTOKENSDATABASE))].index(lptoken_address.lower())
    poolAddress = web3.toChecksumAddress(LPTOKENSDATABASE[index][2])
    tokens = LPTOKENSDATABASE[index][3]
    fraction = amount / totalSupply(web3.toChecksumAddress(lptoken_address), block, blockchain)

    return [[tokens[i], fraction * balanceOf(poolAddress, tokens[i], block, blockchain)] for i in range(len(tokens))]

def poolBalance(lptoken_address, block, blockchain):
    
    web3 = getNode(blockchain, block=block)
    lptoken_address = web3.toChecksumAddress(lptoken_address)

    return LPtokenUnderlying(lptoken_address, totalSupply(lptoken_address, block, blockchain), block, blockchain)

def balanceOfLPtokenUnderlying(address, lptoken_address, block, blockchain):
    
    web3 = getNode(blockchain, block=block)

    return LPtokenUnderlying(web3.toChecksumAddress(lptoken_address),
                             balanceOf(address, web3.toChecksumAddress(lptoken_address), block, blockchain), block)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def isArchival(endpoint):
    web3 = Web3(Web3.HTTPProvider(endpoint))

    try:
        web3.eth.get_balance(ZERO_ADDRESS, block_identifier = 1)
    except ValueError:
        return False
    return True