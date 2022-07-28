from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LITERALS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# API Call - List of the latest pools
API_ELK_POOLS = 'https://api.elk.finance/v2/info/latest_pools'

# Wrapped
WRAPPED = 'wrapped'

# Matic
MATIC = 'matic'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LP Token ABI - decimals, totalSupply, getReserves, balanceOf, token0, token1
ABI_LPTOKEN = '[{"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint8","name":"","internalType":"uint8"}],"name":"decimals","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalSupply","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint112","name":"_reserve0","internalType":"uint112"},{"type":"uint112","name":"_reserve1","internalType":"uint112"},{"type":"uint32","name":"_blockTimestampLast","internalType":"uint32"}],"name":"getReserves","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"balanceOf","inputs":[{"type":"address","name":"","internalType":"address"}],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"address"}],"name":"token0","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"address"}],"name":"token1","inputs":[],"constant":true}]'

# Pool ABI - balanceOf, boosterEarned, boosterToken, earned, rewardsToken, totalSupply 
ABI_POOL = '[{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"balanceOf","inputs":[{"type":"address","name":"account","internalType":"address"}]}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"boosterEarned","inputs":[{"type":"address","name":"account","internalType":"address"}]}, {"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract IERC20"}],"name":"boosterToken","inputs":[]}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"earned","inputs":[{"type":"address","name":"account","internalType":"address"}]}, {"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract IERC20"}],"name":"rewardsToken","inputs":[]}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalSupply","inputs":[]}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPTokenData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPTokenData(web3, lptoken_address, wallet, block, blockchain):

    lptoken_data = {}
     
    lptoken_data['contract'] = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)
    
    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()
    lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])
    lptoken_data['reserves'] = lptoken_data['contract'].functions.getReserves().call(block_identifier = block)
    lptoken_data['token0'] = lptoken_data['contract'].functions.token0().call()
    lptoken_data['token1'] = lptoken_data['contract'].functions.token1().call()
 
    lptoken_data['balanceOf'] = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    return lptoken_data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPoolAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPoolAddress(web3, token0, token1, block, blockchain):

    token0_contract = getContract(token0, blockchain, web3 = web3, abi = ABI_TOKEN_SIMPLIFIED, block = block)
    token1_contract = getContract(token1, blockchain, web3 = web3, abi = ABI_TOKEN_SIMPLIFIED, block = block)

    symbol0 = token0_contract.functions.symbol().call().upper()
    symbol1 = token1_contract.functions.symbol().call().upper()

    if WRAPPED in token0_contract.functions.name().call().lower():
        symbol0 = symbol0[1:len(symbol0)]
    
    if WRAPPED in token1_contract.functions.name().call().lower():
        symbol1 = symbol1[1:len(symbol1)]
    
    if blockchain == POLYGON:
        blockchain = MATIC

    pools = requests.get(API_ELK_POOLS).json()

    try:
        pool_id = symbol0 + '-' + symbol1
        pool_address = pools[blockchain][pool_id]['address']
    
    except:
        try:
            pool_id = symbol1 + '-' + symbol0
            pool_address = pools[blockchain][pool_id]['address']
        
        except:
            pool_address = None

    return pool_address

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getElkRewards
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getElkRewards(web3, pool_contract, wallet, block, blockchain):

    elk_token_address = pool_contract.functions.rewardsToken().call()

    elk_token_decimals = getDecimals(elk_token_address, blockchain, web3 = web3)
    
    elk_rewards = pool_contract.functions.earned(wallet).call(block_identifier = block) / (10**elk_token_decimals)
    
    return [elk_token_address, elk_rewards]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getBoosterRewards
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getBoosterRewards(web3, pool_contract, wallet, block, blockchain):

    booster_token_address = pool_contract.functions.boosterToken().call()

    booster_token_decimals = getDecimals(booster_token_address, blockchain, web3 = web3)
    
    booster_rewards = pool_contract.functions.boosterEarned(wallet).call(block_identifier = block) / (10**booster_token_decimals)
    
    return [booster_token_address, booster_rewards]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'pool_contract' -> Improves performance
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getAllRewards(wallet, lptoken_address, block, blockchain, **kwargs):

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
        
        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)

        try:
            pool_contract = kwargs['pool_contract']
        except:
            lptoken_data = getLPTokenData(web3, lptoken_address, wallet, block, blockchain)

            pool_address = getPoolAddress(web3, lptoken_data['token0'], lptoken_data['token1'], block, blockchain)
            pool_contract = getContract(pool_address, blockchain, web3 = web3, abi = ABI_POOL, block = block)

        elk_rewards = getElkRewards(web3, pool_contract, wallet, block, blockchain)
        all_rewards.append(elk_rewards)
        
        booster_rewards = getBoosterRewards(web3, pool_contract, wallet, block, blockchain)
        all_rewards.append(booster_rewards)
        
        return all_rewards

    except GetNodeLatestIndexError:
        index = 0

        return getAllRewards(wallet, lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0

        return getAllRewards(wallet, lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except Exception:
        return getAllRewards(wallet, lptoken_address, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ElkUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance]
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ElkUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

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
        
        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)
        
        lptoken_data = getLPTokenData(web3, lptoken_address, wallet, block, blockchain)

        pool_address = getPoolAddress(web3, lptoken_data['token0'], lptoken_data['token1'], block, blockchain)

        if pool_address == None:
            print('Error: Cannot find Elk Pool Address for LPToken Address: ', lptoken_address)
            return None

        pool_contract = getContract(pool_address, blockchain, web3 = web3, abi = ABI_POOL, block = block)

        pool_balance_fraction = lptoken_data['balanceOf'] / lptoken_data['totalSupply']
        pool_staked_fraction =  pool_contract.functions.balanceOf(wallet).call(block_identifier = block) / pool_contract.functions.totalSupply().call(block_identifier = block)

        for i in range(len(lptoken_data['reserves']) - 1):
            
            if i == 0:
                token_address = lptoken_data['token0']
            
            elif i == 1:
                token_address = lptoken_data['token1']
            
            token_decimals = getDecimals(token_address, blockchain, web3 = web3)

            token_balance = lptoken_data['reserves'][i] / (10**token_decimals) * (pool_balance_fraction)
            token_staked = lptoken_data['reserves'][i] / (10**token_decimals) * (pool_staked_fraction)

            balances.append([token_address, token_balance, token_staked])
        
        if reward == True:
            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, pool_contract = pool_contract)
            
            result.append(balances)
            result.append(all_rewards)
       
        else:
            result = balances

        return result

    except GetNodeLatestIndexError:
        index = 0

        return ElkUnderlying(wallet, lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return ElkUnderlying(wallet, lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return ElkUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ElkPoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ElkPoolBalances(lptoken_address, block, blockchain, **kwargs):

    balances = []

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
        web3 = getNode(blockchain, block = block, index = index)
        
        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)
        
        lptoken_contract = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)

        reserves = lptoken_contract.functions.getReserves().call(block_identifier = block)

        for i in range(len(reserves) - 1):
            try:
                func = getattr(lptoken_contract.functions, 'token' + str(i))
            except:
                continue

            token_address = func().call()
            token_decimals = getDecimals(token_address, blockchain, web3 = web3)

            token_balance = reserves[i] / (10 ** token_decimals)

            balances.append([token_address, token_balance])

        return balances

    except GetNodeLatestIndexError:
        index = 0

        return ElkPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return ElkPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return ElkPoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)