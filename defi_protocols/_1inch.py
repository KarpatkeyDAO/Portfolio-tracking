from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ORACLES
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ethereum Oracle Address
ORACLE_ETHEREUM = '0x07D91f5fb9Bf7798734C3f606dB065549F6893bb'

# Polygon Oracle Address
ORACLE_POLYGON = '0x7F069df72b7A39bCE9806e3AfaF579E54D8CF2b9'

# Gnosis Chain(xDai) Oracle Address
ORACLE_XDAI = '0x142DB045195CEcaBe415161e1dF1CF0337A4d02E'

# Smart Chain (Binance) Oracle Address
ORACLE_BINANCE = '0xfbD61B037C325b959c0F6A7e69D8f37770C2c550'

# Kovan Oracle Address
ORACLE_KOVAN = '0x29BC86Ad68bB3BD3d54841a8522e0020C1882C22'

# Optimism Oracle Address
ORACLE_OPTIMISM = '0x11DEE30E710B8d4a8630392781Cc3c0046365d4c'

# Arbitrum Oracle Address
ORACLE_ARBITRUM = '0x735247fb0a604c0adC6cab38ACE16D0DbA31295F'

# Avax Oracle Address
ORACLE_AVAX = '0xBd0c7AaF0bF082712EbE919a9dD94b2d978f79A9'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CHAINLINK PRICE FEEDS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETHEREUM
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
# Oracle ABI - connectors, oracles, getRate, getRateToEth
ABI_ORACLE = '[{"inputs":[],"name":"connectors","outputs":[{"internalType":"contract IERC20[]","name":"allConnectors","type":"address[]"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"oracles","outputs":[{"internalType":"contract IOracle[]","name":"allOracles","type":"address[]"},{"internalType":"enum OffchainOracle.OracleType[]","name":"oracleTypes","type":"uint8[]"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"contract IERC20","name":"dstToken","type":"address"},{"internalType":"bool","name":"useWrappers","type":"bool"}],"name":"getRate","outputs":[{"internalType":"uint256","name":"weightedRate","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"bool","name":"useSrcWrappers","type":"bool"}],"name":"getRateToEth","outputs":[{"internalType":"uint256","name":"weightedRate","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# ChainLink Price Feed ABI - latestAnswer, decimals
ABI_CHAINLINK_PRICE_FEED = '[{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getOracleAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getOracleAddress(blockchain):

    if blockchain == ETHEREUM:
        return ORACLE_ETHEREUM

    elif blockchain == POLYGON:
        return ORACLE_POLYGON

    elif blockchain == XDAI:
        return ORACLE_XDAI

    elif blockchain == BINANCE:
        return ORACLE_BINANCE

    elif blockchain == KOVAN:
        return ORACLE_KOVAN

    elif blockchain == OPTIMISM:
        return ORACLE_OPTIMISM
    
    elif blockchain == ARBITRUM:
        return ORACLE_ARBITRUM
    
    elif blockchain == AVAX:
        return ORACLE_AVAX

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getNativeTokenPrice
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getNativeTokenPrice(web3, block, blockchain):

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
# getRate1inch
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'token_dst' = token_dst address -> if it's not passed onto the function, the native token of the blockchain is used to calculate the rate
# 'use_wrappers' = True / False -> To handle wrapped tokens, such as wETH, cDAI, aDAI etc., the 1inch spot price aggregator uses custom wrapper smart contracts that 
#                                  wrap/unwrap tokens at the current wrapping exchange rate
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getRate1inch(token_src, block, blockchain, **kwargs):

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
        use_wrappers = kwargs['use_wrappers']
    except:
        use_wrappers = False
    
    try:
        token_dst = kwargs['token_dst']
    except:
        token_dst = None
    
    try:
        web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(token_src):
            token_src = web3.toChecksumAddress(token_src)
        
        if token_dst != None:
            if not web3.isChecksumAddress(token_dst):
                token_dst = web3.toChecksumAddress(token_dst)
        
        oracle_address = getOracleAddress(blockchain)
        oracle_contract = getContract(oracle_address, blockchain, web3 = web3, abi = ABI_ORACLE, block = block)

        token_src_decimals = getDecimals(token_src, blockchain, web3 = web3)

        if token_dst != None:
            token_dst_decimals = getDecimals(token_dst, blockchain, web3 = web3)
        else:
            token_dst_decimals = 18

        if token_dst == None:
            rate = oracle_contract.functions.getRateToEth(token_src, use_wrappers).call(block_identifier = block) / (10**abs(18 + token_dst_decimals - token_src_decimals))
        else:
            rate = oracle_contract.functions.getRate(token_src, token_dst, use_wrappers).call(block_identifier = block) / (10**abs(18 + token_dst_decimals - token_src_decimals))

        return rate
    
    except GetNodeLatestIndexError:
        index = 0

        return getRate1inch(token_src, token_dst, block, blockchain, index = index, execution = execution + 1, use_wrappers = use_wrappers)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return getRate1inch(token_src, token_dst, block, blockchain, index = index, execution = execution + 1, use_wrappers = use_wrappers)

    except Exception:
        return getRate1inch(token_src, token_dst, block, blockchain, index = index + 1, execution = execution, use_wrappers = use_wrappers)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPrice1inch
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'connector' = connector address -> if it's not passed onto the function, the native token of the blockchain is used to calculate the token_src price /
#                                    if it's passed onto the function, the connector is used to calculate the token_src price
# 'use_wrappers' = True / False -> To handle wrapped tokens, such as wETH, cDAI, aDAI etc., the 1inch spot price aggregator uses custom wrapper smart contracts that 
#                                  wrap/unwrap tokens at the current wrapping exchange rate
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPrice1inch(token_src, block, blockchain, **kwargs):

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
        connector = kwargs['connector']
    except:
        connector = None
    
    try:
        use_wrappers = kwargs['use_wrappers']
    except:
        use_wrappers = False

    try:
        web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(token_src):
            token_src = web3.toChecksumAddress(token_src)
        
        native_token_price = getNativeTokenPrice(web3, block, blockchain)

        if token_src == ZERO_ADDRESS:
            return native_token_price
        
        else:
            if connector == None:
                rate = getRate1inch(token_src, block, blockchain, use_wrappers = use_wrappers)
                token_src_price = native_token_price * rate
            else:
                if not web3.isChecksumAddress(connector):
                    connector = web3.toChecksumAddress(connector)

                rate = getRate1inch(token_src, block, blockchain, token_dst = connector, use_wrappers = use_wrappers)
                connector_price = getPrice1inch(connector, block, blockchain, use_wrappers = use_wrappers)
                token_src_price = connector_price * rate

        return token_src_price
    
    except GetNodeLatestIndexError:
        index = 0

        return getPrice1inch(token_src, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return getPrice1inch(token_src, block, blockchain, index = index, execution = execution + 1)

    except Exception:
       return getPrice1inch(token_src, block, blockchain, index = index + 1, execution = execution)



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getFuckingPrice(address, block, blockchain):

    if blockchain == XDAI:
        return getPrice1inch(address, block, blockchain)

    else:
        web3 = getNode(ETHEREUM, block = block)
        FeedRegistryContract = getContract(web3.toChecksumAddress('0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf'), ETHEREUM, block = block)

        try:
            FeedContractUSD_address = FeedRegistryContract.functions.getFeed(address, '0x0000000000000000000000000000000000000348').call(block_identifier=block)
            FeedContract = getContract(FeedContractUSD_address, ETHEREUM, block = block)
            decimals = FeedContract.functions.decimals().call(block_identifier = block)
            return FeedContract.functions.latestAnswer().call(block_identifier = block)/10**decimals
        except:
            try:
                FeedContractETH_address = FeedRegistryContract.functions.getFeed(address,'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE').call(
                    block_identifier=block)
                FeedContractETH = getContract(FeedContractETH_address, ETHEREUM, block=block)
                decimals = FeedContractETH.functions.decimals().call(block_identifier=block)
                return FeedContractETH.functions.latestAnswer().call(block_identifier = block)/10**decimals*getNativeTokenPrice(web3, block, ETHEREUM)
            except:
                if block == 'latest':
                    block = lastBlock(ETHEREUM)
                price_coingecko = getPriceCoinGecko(address, blockToTimestamp(block, ETHEREUM),ETHEREUM)
                if price_coingecko[0] == 200:
                    return price_coingecko[1][1]
                else:
                    return getPrice1inch(address, block, ETHEREUM)