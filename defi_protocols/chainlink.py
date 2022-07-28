from defi_protocols._1inch import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CHAINLINK PRICE FEEDS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETHEREUM
# Feed Registry
CHAINLINK_FEED_REGISTRY = '0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf'
# Quotes - USD and ETH
CHAINLINK_ETH_QUOTES = ['0x0000000000000000000000000000000000000348', '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE']
# ETH/USD Price Feed
CHAINLINK_ETH_USD = '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'

# POLYGON
# MATIC/USD Price Feed
CHAINLINK_MATIC_USD = '0xAB594600376Ec9fD91F8e885dADF0CE036862dE0'

# XDAI
# XDAI/USD Price Feed - The price feed retrieves the price of DAI instead of XDAI. Chainlink does not provide a price feed for XDAI.
CHAINLINK_XDAI_USD = '0x678df3415fc31947dA4324eC63212874be5a82f8'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ChainLink Feed Registry ABI - getFeed
ABI_CHAINLINK_FEED_REGISTRY = '[{"inputs":[{"internalType":"address","name":"base","type":"address"},{"internalType":"address","name":"quote","type":"address"}],"name":"getFeed","outputs":[{"internalType":"contract AggregatorV2V3Interface","name":"aggregator","type":"address"}],"stateMutability":"view","type":"function"}]'
# ChainLink Price Feed ABI - latestAnswer, decimals
ABI_CHAINLINK_PRICE_FEED = '[{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getNativeTokenPriceChainLink
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getNativeTokenPriceChainLink(web3, block, blockchain):

    if blockchain == ETHEREUM:
        price_feed_address = CHAINLINK_ETH_USD
    
    elif blockchain == POLYGON:
        price_feed_address = CHAINLINK_MATIC_USD
    
    elif blockchain == XDAI:
        price_feed_address = CHAINLINK_XDAI_USD

    price_feed_contract = getContract(price_feed_address, blockchain, web3 = web3, abi = ABI_CHAINLINK_PRICE_FEED, block = block)
    price_feed_decimals = price_feed_contract.functions.decimals().call()
    native_token_price = price_feed_contract.functions.latestAnswer().call(block_identifier = block) / (10**price_feed_decimals)

    return native_token_price

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getMainnetPriceChainLink
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getMainnetPriceChainLink(token_address, block, **kwargs):

    try:
        execution = kwargs['execution']
    except:
        execution = 1

    # If the number of executions is greater than the MAX_EXECUTIONS variable -> returns None and halts
    if execution > MAX_EXECUTIONS:
        return None

    try:
        index = kwargs['index']
    except:
        index = 0
    
    try:
        web3 = getNode(ETHEREUM, block = block, index = index)

        if not web3.isChecksumAddress(token_address):
            token_address = web3.toChecksumAddress(token_address)

        feed_registry_contract = getContract(CHAINLINK_FEED_REGISTRY, ETHEREUM, web3 = web3, abi = ABI_CHAINLINK_FEED_REGISTRY, block = block)

        for quote in CHAINLINK_ETH_QUOTES:
            try:
                price_feed_address = feed_registry_contract.functions.getFeed(token_address, quote).call(block_identifier = block)
                price_feed_contract = getContract(price_feed_address, ETHEREUM, web3 = web3, abi = ABI_CHAINLINK_PRICE_FEED, block = block)
                price_feed_decimals = price_feed_contract.functions.decimals().call()
                
                if quote == CHAINLINK_ETH_QUOTES[0]:
                    return price_feed_contract.functions.latestAnswer().call(block_identifier = block) / 10**price_feed_decimals
                else:
                    return price_feed_contract.functions.latestAnswer().call(block_identifier = block) / 10**price_feed_decimals * getNativeTokenPriceChainLink(web3, block, ETHEREUM)

            except Exception as ex:
                if 'Feed not found' in ex.args[0]:
                    continue
                else:
                    raise Exception
        
        return None

    except GetNodeLatestIndexError:
        index = 0

        return getMainnetPriceChainLink(token_address, block, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return getMainnetPriceChainLink(token_address, block, index = index, execution = execution + 1)

    except Exception:
        return getMainnetPriceChainLink(token_address, block, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPrice
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPrice(token_address, block, blockchain, **kwargs):

    try:
        token_mapping_data = kwargs['token_mapping_data']
    except:
        token_mapping_data = None

    token_price = None

    web3 = getNode(ETHEREUM)
    token_address = web3.toChecksumAddress(token_address)

    if block == 'latest':
        block = lastBlock(blockchain)

    # COW is treated as a particular case
    if token_address == COW_XDAI:
        return getPrice1inch(token_address, block, XDAI, connector = GNO_XDAI)
    if token_address == COW_ETH:
        block = timestampToBlock(blockToTimestamp(block, ETHEREUM), XDAI)
        return getPrice1inch(COW_XDAI, block, XDAI, connector = GNO_XDAI)

    # sGNO is treated as a particular case
    if token_address == '0xA4eF9Da5BA71Cc0D2e5E877a910A37eC43420445':
        return getPrice1inch(token_address, block, XDAI, connector=GNO_XDAI)

    # rGNO is treated as a particular case
    if token_address == '0x6aC78efae880282396a335CA2F79863A1e6831D4':
        return getPrice1inch(token_address, block, XDAI, connector=GNO_XDAI)

    #SWPR is treated as a particular case
    if token_address == '0x532801ED6f82FFfD2DAB70A19fC2d7B2772C4f4b':
        return getPrice1inch(token_address, block, XDAI)
    if token_address == '0x6cAcDB97e3fC8136805a9E7c342d866ab77D0957':
        block = timestampToBlock(blockToTimestamp(block, ETHEREUM), XDAI)
        return getPrice1inch('0x532801ED6f82FFfD2DAB70A19fC2d7B2772C4f4b', block, XDAI)

    #GIV is treated as a particular case
    if token_address == '0x4f4F9b8D5B4d0Dc10506e5551B0513B61fD59e75':
        return getPrice1inch(token_address, block, XDAI)
    if token_address == '0xf6537FE0df7F0Cc0985Cf00792CC98249E73EFa0':
        block = timestampToBlock(blockToTimestamp(block, ETHEREUM), XDAI)
        return getPrice1inch('0x4f4F9b8D5B4d0Dc10506e5551B0513B61fD59e75', block, XDAI)

    if blockchain != ETHEREUM:
        block_eth = timestampToBlock(blockToTimestamp(block, blockchain), ETHEREUM)

        if token_mapping_data == None:
            with open('../db/token_mapping.json', 'r') as token_mapping_file:
                # Reading from json file
                token_mapping_data = json.load(token_mapping_file)
    
        try:
            token_address_eth = token_mapping_data[blockchain][token_address][ETHEREUM]
        except:
            token_address_eth = None
    
    else:
        token_address_eth = token_address
        block_eth = block
    
    if token_address_eth != None:
        token_price = getMainnetPriceChainLink(token_address_eth, block_eth)

        if token_price == None:
            token_price = getPrice1inch(token_address_eth, block_eth, ETHEREUM)
    
    else:
        if blockchain == XDAI:
            token_price = getPrice1inch(token_address, block, blockchain, connector = GNO_XDAI)
        else:
            token_price = getPrice1inch(token_address, block, blockchain)

    return token_price

