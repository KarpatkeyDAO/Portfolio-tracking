from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PROTOCOL DATA PROVIDER
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Protocol Data Provider - Ethereum
PDP_ETHEREUM = '0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LENDING POOL ADDRESSES PROVIDER REGISTRY
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Lending Pool Addresses Provider Registry - Ethereum
LPAPR_ETHEREUM = '0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CHAINLINK PRICE FEEDS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETHEREUM
# ETH/USD Price Feed
CHAINLINK_ETH_USD = '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Protocol Data Provider ABI - getAllReservesTokens, getUserReserveData
ABI_PDP = '[{"inputs":[],"name":"getAllReservesTokens","outputs":[{"components":[{"internalType":"string","name":"symbol","type":"string"},{"internalType":"address","name":"tokenAddress","type":"address"}],"internalType":"struct AaveProtocolDataProvider.TokenData[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"user","type":"address"}],"name":"getUserReserveData","outputs":[{"internalType":"uint256","name":"currentATokenBalance","type":"uint256"},{"internalType":"uint256","name":"currentStableDebt","type":"uint256"},{"internalType":"uint256","name":"currentVariableDebt","type":"uint256"},{"internalType":"uint256","name":"principalStableDebt","type":"uint256"},{"internalType":"uint256","name":"scaledVariableDebt","type":"uint256"},{"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},{"internalType":"uint256","name":"liquidityRate","type":"uint256"},{"internalType":"uint40","name":"stableRateLastUpdated","type":"uint40"},{"internalType":"bool","name":"usageAsCollateralEnabled","type":"bool"}],"stateMutability":"view","type":"function"}]'

# Lending Pool Addresses Provider Registry ABI - getLendingPool, getPriceOracle
ABI_LPAPR = '[{"inputs":[],"name":"getLendingPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getPriceOracle","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

# Lending Pool ABI - getUserAccountData
ABI_LENDING_POOL = '[{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralETH","type":"uint256"},{"internalType":"uint256","name":"totalDebtETH","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsETH","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# ChainLink: ETH/USD Price Feed ABI - latestAnswer, decimals
ABI_CHAINLINK_ETH_USD = '[{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}]'

# Price Oracle ABI - getAssetPrice
ABI_PRICE_ORACLE = '[{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getAssetPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Staked Aave ABI - REWARD_TOKEN, getTotalRewardsBalance
ABI_STK_AAVE = '[{"inputs":[],"name":"REWARD_TOKEN","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"staker","type":"address"}],"name":"getTotalRewardsBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getProtocolDataProvider
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getProtocolDataProvider(blockchain):

    if blockchain == ETHEREUM:
        return PDP_ETHEREUM

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPAPRAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPAPRAddress(blockchain):

    if blockchain == ETHEREUM:
        return LPAPR_ETHEREUM

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getReservesTokens
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getReservesTokens(pdp_contract):

    reserves_tokens_addresses = []
    
    reserves_tokens = pdp_contract.functions.getAllReservesTokens().call()

    for reserves_token in reserves_tokens:
        reserves_tokens_addresses.append(reserves_token[1])
    
    return reserves_tokens_addresses

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getReservesTokensBalances
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getReservesTokensBalances(web3, wallet, block, blockchain):

    balances = []

    pdp_address = getProtocolDataProvider(blockchain)
    pdp_contract = getContract(pdp_address, blockchain, web3 = web3, abi = ABI_PDP, block = block)
    
    reserves_tokens = getReservesTokens(pdp_contract)

    for reserves_token in reserves_tokens:

        try:
            user_reserve_data = pdp_contract.functions.getUserReserveData(reserves_token, wallet).call(block_identifier = block)
        except:
            continue
            
        token_decimals = getDecimals(reserves_token, blockchain, web3 = web3)

        # balance = currentATokenBalance - currentStableDebt - currentStableDebt
        balance = (user_reserve_data[0] - user_reserve_data[1] - user_reserve_data[2]) / 10**token_decimals

        if balance != 0:              
            balances.append([reserves_token, balance])
    
    return balances

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAaveData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getAaveData(wallet, block, blockchain, **kwargs):

    aave_data = {}
    collaterals = []
    debts = []

    try:
        execution = kwargs['execution']
    except:
        execution = 1

    # If the number of executions is greater than the MAX_EXECUTIONS variable -> returns None and halts   
    if execution > MAX_EXECUTIONS:
        return None

    try:
        web3 = kwargs['web3']
    except:
        web3 = None

    try:
        index = kwargs['index']
    except:
        index = 0
    
    try:
        if web3 == None: 
            web3 = getNode(blockchain, block = block, index = index)
        
        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)
        
        lpapr_address = getLPAPRAddress(blockchain)
        lpapr_contract = getContract(lpapr_address, blockchain, web3 = web3, abi = ABI_LPAPR, block = block)

        lending_pool_address = lpapr_contract.functions.getLendingPool().call()
        lending_pool_contract = getContract(lending_pool_address, blockchain, web3 = web3, abi = ABI_LENDING_POOL, block = block)

        chainlink_eth_usd_contract = getContract(CHAINLINK_ETH_USD, blockchain, web3 = web3, abi = ABI_CHAINLINK_ETH_USD, block = block)
        chainlink_eth_usd_decimals = chainlink_eth_usd_contract.functions.decimals().call()
        eth_usd_price = chainlink_eth_usd_contract.functions.latestAnswer().call(block_identifier = block) / (10**chainlink_eth_usd_decimals)

        balances = getReservesTokensBalances(web3, wallet, block, blockchain)

        if len(balances) > 0:

            price_oracle_address = lpapr_contract.functions.getPriceOracle().call()
            price_oracle_contract = getContract(price_oracle_address, blockchain, web3 = web3, abi = ABI_PRICE_ORACLE, block = block)

            for balance in balances:
                asset = {}

                asset['token_address'] = balance[0]
                asset['token_amount'] = abs(balance[1])
                asset['token_price_usd'] = price_oracle_contract.functions.getAssetPrice(asset['token_address']).call(block_identifier = block) / (10**18) * eth_usd_price
                
                if balance[1] < 0:
                    debts.append(asset)   
                else:
                    collaterals.append(asset)

        # getUserAccountData return a list with the following data:
        # [0] = totalCollateralETH, [1] = totalDebtETH, [2] = availableBorrowsETH, [3] = currentLiquidationThreshold, [4] = ltv, [5] = healthFactor 
        user_account_data = lending_pool_contract.functions.getUserAccountData(wallet).call(block_identifier = block)

        # Collateral Ratio
        aave_data['collateral_ratio'] = (user_account_data[0] / user_account_data[1]) * 100

        # Liquidation Ratio
        aave_data['liquidation_ratio'] = (1 / user_account_data[3]) * 1000000

        # Ether price in USD
        aave_data['eth_price_usd'] = eth_usd_price

        # Collaterals Data
        aave_data['collaterals'] = collaterals

        # Debts Data
        aave_data['debts'] = debts

        return aave_data
    
    except GetNodeLatestIndexError:
        index = 0

        return getAaveData(wallet, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0

        return getAaveData(wallet, block, blockchain, index = index, execution = execution + 1)
    
    except Exception:
        return getAaveData(wallet, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getAllRewards(wallet, block, blockchain, **kwargs):

    all_rewards = []

    try:
        execution = kwargs['execution']
    except:
        execution = 1

    # If the number of executions is greater than the MAX_EXECUTIONS variable -> returns None and halts   
    if execution > MAX_EXECUTIONS:
        return None

    try:
        web3 = kwargs['web3']
    except:
        web3 = None

    try:
        index = kwargs['index']
    except:
        index = 0
    
    try:
        if web3 == None: 
            web3 = getNode(blockchain, block = block, index = index)
        
        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)

        if blockchain == ETHEREUM:
            stk_aave_contract = getContract(STK_AAVE_ETH, blockchain, web3 = web3, abi = ABI_STK_AAVE, block = block)

            reward_token = stk_aave_contract.functions.REWARD_TOKEN().call()
            reward_token_decimals = getDecimals(reward_token, blockchain, web3 = web3)
            reward_balance = stk_aave_contract.functions.getTotalRewardsBalance(wallet).call(block_identifier = block) / (10**reward_token_decimals)

            all_rewards.append([reward_token, reward_balance])

        if len(all_rewards) == 0:
            return []
        elif len(all_rewards) == 1:
            return all_rewards.pop()
        else:
            return all_rewards

    except GetNodeLatestIndexError:
        index = 0

        return getAllRewards(wallet, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0

        return getAllRewards(wallet, block, blockchain, index = index, execution = execution + 1)
    
    except Exception:
        return getAllRewards(wallet, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# AaveUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [token_address, balance], where balance = currentATokenBalance - currentStableDebt - currentStableDebt
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def AaveUnderlying(wallet, block, blockchain, **kwargs):

    result = []
    balances = []

    try:
        execution = kwargs['execution']
    except:
        execution = 1

    # If the number of executions is greater than the MAX_EXECUTIONS variable -> returns None and halts
    if execution > MAX_EXECUTIONS:
        return None

    try:
        reward = kwargs['reward']
    except:
        reward = False

    try:
        index = kwargs['index']
    except:
        index = 0

    try:
        web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)
        
        balances = getReservesTokensBalances(web3, wallet, block, blockchain)
     
        if reward == True:
            all_rewards = getAllRewards(wallet, block, blockchain, web3 = web3, index = index)
            
            result.append(balances)
            result.append(all_rewards)
       
        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return AaveUnderlying(wallet, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return AaveUnderlying(wallet, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return AaveUnderlying(wallet, block, blockchain, index = index + 1, reward = reward, execution = execution)