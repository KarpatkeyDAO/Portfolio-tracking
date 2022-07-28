from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MASTERCHEF_V1
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MASTERCHEF_V1 Contract Address
MASTERCHEF_V1 = '0xc2EdaD668740f1aA35E4D8f227fB8E17dcA888Cd'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MASTERCHEF_V2
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MASTERCHEF_V2 Contract Address
MASTERCHEF_V2 = '0xEF0881eC094552b2e128Cf945EF17a6752B4Ec5d'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LIQUIDITY MINING
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Polygon - MiniChef Contract Address
MINICHEF_POLYGON = '0x0769fd68dFb93167989C6f7254cd0D766Fb2841F'

# xDAI - MiniChef Contract Address
MINICHEF_XDAI = '0xdDCbf776dF3dE60163066A5ddDF2277cB445E0F3'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Chefs V2 ABI - SUSHI, rewarder, pendingSushi, lpToken, userInfo, poolLength
ABI_CHEF_V2 = '[{"inputs":[],"name":"SUSHI","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"rewarder","outputs":[{"internalType":"contract IRewarder","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"_pid","type":"uint256"},{"internalType":"address","name":"_user","type":"address"}],"name":"pendingSushi","outputs":[{"internalType":"uint256","name":"pending","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"lpToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"name":"userInfo","outputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"int256","name":"rewardDebt","type":"int256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"poolLength","outputs":[{"internalType":"uint256","name":"pools","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Chefs V1 ABI - sushi, rewarder, pendingSushi, poolInfo, userInfo, poolLength
ABI_CHEF_V1 = '[{"inputs":[],"name":"sushi","outputs":[{"internalType":"contract SushiToken","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"rewarder","outputs":[{"internalType":"contract IRewarder","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"_pid","type":"uint256"},{"internalType":"address","name":"_user","type":"address"}],"name":"pendingSushi","outputs":[{"internalType":"uint256","name":"pending","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"poolInfo","outputs":[{"internalType":"contract IERC20","name":"lpToken","type":"address"},{"internalType":"uint256","name":"allocPoint","type":"uint256"},{"internalType":"uint256","name":"lastRewardBlock","type":"uint256"},{"internalType":"uint256","name":"accSushiPerShare","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"name":"userInfo","outputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"int256","name":"rewardDebt","type":"int256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"poolLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Rewarder ABI - rewardToken, pendingTokens
ABI_REWARDER = '[{"inputs":[{"internalType":"uint256","name":"pid","type":"uint256"},{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"pendingTokens","outputs":[{"internalType":"contract IERC20[]","name":"rewardTokens","type":"address[]"},{"internalType":"uint256[]","name":"rewardAmounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]'

# LP Token ABI - decimals, totalSupply, getReserves, balanceOf, token0, token1
ABI_LPTOKEN = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getChefContract
# **kwargs: 
# 'v1' = True -> If blockchain = ETHEREUM retrieves the MASTERCHEF_V1 Contract / 'v1' = False or not passed onto the function -> retrieves the MASTERCHEF_V2 Contract
# Output: chef_contract
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getChefContract(web3, block, blockchain, **kwargs):

    # try: If kwargs['v1'] is passed onto the function or not
    try:
        v1 = kwargs['v1']
    except:
    # If kwargs['v1'] is not passed onto the function then v1 = False
        v1 = False

    if blockchain == ETHEREUM:
        if v1 == False:
            chef_contract = getContract(MASTERCHEF_V2, blockchain, web3 = web3, abi = ABI_CHEF_V2, block = block)
        else:
            chef_contract = getContract(MASTERCHEF_V1, blockchain, web3 = web3, abi = ABI_CHEF_V1, block = block)
    
    elif blockchain == POLYGON:
        chef_contract = getContract(MINICHEF_POLYGON, blockchain, web3 = web3, abi = ABI_CHEF_V2, block = block)
    
    elif blockchain == XDAI:
        chef_contract = getContract(MINICHEF_XDAI, blockchain, web3 = web3, abi = ABI_CHEF_V2, block = block)

    return chef_contract

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPoolInfo
# Output:
# 1 - Tuple: [chef_contractV1 | chef_contractV2, pool_id] - chef_contractV1 | chef_contractV2 depending on whether the pool is V1 or V2
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPoolInfo(web3, lptoken_address, block, blockchain):

    chef_contract = getChefContract(web3, block, blockchain)

    with open('../db/sushi_swap.json', 'r') as db_file:
        # Reading from json file
        db_data = json.load(db_file)
    
    if blockchain == ETHEREUM:
        try:
            db_data[blockchain]['poolsv2'][lptoken_address]
            return [chef_contract, db_data[blockchain]['poolsv2'][lptoken_address]]
        
        except:
            try:
                db_data[blockchain]['poolsv1'][lptoken_address]
                chef_contract = getChefContract(web3, block, blockchain, v1 = True)

                return [chef_contract, db_data[blockchain]['poolsv1'][lptoken_address]]
            
            except:
                return [None, -1]
    
    else:
        try:
            db_data[blockchain]['pools'][lptoken_address]
            if blockchain == POLYGON:
                return [chef_contract, db_data[blockchain]['pools'][lptoken_address]]
            
            elif blockchain == XDAI:
                return [chef_contract, db_data[blockchain]['pools'][lptoken_address]]
        except:
            return [None, -1]

    # chef_contract = getChefContract(web3, block, blockchain)

    # pool_length = chef_contract.functions.poolLength().call(block_identifier = block)

    # for pool_id in range(pool_length):

    #     address = chef_contract.functions.lpToken(pool_id).call()

    #     if address == lptoken_address:
    #         return [chef_contract, pool_id]
    
    # # This section searches if the pool it's a V1 pool (only in ETHEREUM)
    # if blockchain == ETHEREUM:

    #     chef_contract = getChefContract(web3, block, blockchain, v1 = True)

    #     pool_length = chef_contract.functions.poolLength().call(block_identifier = block)

    #     for pool_id in range(pool_length):

    #         address = chef_contract.functions.poolInfo(pool_id).call()[0]

    #         if address == lptoken_address:
    #             return [chef_contract, pool_id]
    
    # # If the lptoken_address doesn't match with a V2 or V1 pool
    # return [None, -1]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPTokenData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPTokenData(web3, chef_contract, lptoken_address, pool_id, wallet, block, blockchain):

    lptoken_data = {}
     
    lptoken_data['contract'] = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)
    
    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()
    lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])
    lptoken_data['reserves'] = lptoken_data['contract'].functions.getReserves().call(block_identifier = block)

    lptoken_data['staked'] = chef_contract.functions.userInfo(pool_id, wallet).call(block_identifier = block)[0] / (10**lptoken_data['decimals'])
    lptoken_data['balanceOf'] = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    return lptoken_data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getSushiRewards
# Output:
# 1 - Tuple: [sushi_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getSushiRewards(web3, wallet, chef_contract, pool_id, block, blockchain):
    
    try:
        sushi_token_address = chef_contract.functions.SUSHI().call()
    except:
        sushi_token_address = chef_contract.functions.sushi().call()

    sushi_token_decimals = getDecimals(sushi_token_address, blockchain, web3 = web3)
    
    sushi_rewards = chef_contract.functions.pendingSushi(pool_id, wallet).call(block_identifier = block) / (10**sushi_token_decimals)

    return [sushi_token_address, sushi_rewards]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getRewarderContract
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getRewarderContract(web3, block, blockchain, chef_contract, pool_id):

    rewarder_contract_address = chef_contract.functions.rewarder(pool_id).call()
    rewarder_contract = getContract(rewarder_contract_address, blockchain, web3 = web3, abi = ABI_REWARDER, block = block)
    
    return rewarder_contract

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getRewards
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getRewards(web3, wallet, chef_contract, pool_id, block, blockchain):

    rewards = []

    rewarder_contract = getRewarderContract(web3, block, blockchain, chef_contract, pool_id)

    pending_tokens_info = rewarder_contract.functions.pendingTokens(pool_id, wallet, 1).call(block_identifier = block)
    pending_tokens_addresses = pending_tokens_info[0]
    pending_token_amounts = pending_tokens_info[1]

    for i in range(len(pending_tokens_addresses)):

        reward_token_decimals = getDecimals(pending_tokens_addresses[i], blockchain, web3 = web3)
        reward_token_amount = pending_token_amounts[i] / (10**reward_token_decimals)

        rewards.append([pending_tokens_addresses[i], reward_token_amount])

    return rewards

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'pool_info' = [chef_contract, pool_id] -> Improves performance
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
            pool_info = kwargs['pool_info']
        except:
            pool_info = getPoolInfo(web3, lptoken_address, block, blockchain)

        pool_id = pool_info[1]
        chef_contract = pool_info[0]

        if pool_id == -1:
            print('Error: Incorrect Sushi LPToken Address: ', lptoken_address)
            return None

        sushi_rewards = getSushiRewards(web3, wallet, chef_contract, pool_id, block, blockchain)
        all_rewards.append(sushi_rewards)

        if chef_contract.address != MASTERCHEF_V1:
            rewards = getRewards(web3, wallet, chef_contract, pool_id, block, blockchain)

            if len(rewards) > 0:
                for reward in rewards:
                    all_rewards.append(reward)

        if len(all_rewards) == 0:
            return []
        elif len(all_rewards) == 1:
            return all_rewards.pop()
        else:
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
# SushiSwapUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance]
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def SushiSwapUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

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

        pool_info = getPoolInfo(web3, lptoken_address, block, blockchain)

        chef_contract = pool_info[0]
        pool_id = pool_info[1]

        if pool_id == -1:
            print('Error: Incorrect Sushi LPToken Address: ', lptoken_address)
            return None

        lptoken_data = getLPTokenData(web3, chef_contract, lptoken_address, pool_id, wallet, block, blockchain)

        pool_balance_fraction = lptoken_data['balanceOf'] / lptoken_data['totalSupply']
        pool_staked_fraction =  lptoken_data['staked'] / lptoken_data['totalSupply']

        for i in range(len(lptoken_data['reserves'])):
            try:
                func = getattr(lptoken_data['contract'].functions, 'token' + str(i))
            except:
                continue
            
            token_address = func().call()
            token_decimals = getDecimals(token_address, blockchain, web3 = web3)

            token_balance = lptoken_data['reserves'][i] / (10**token_decimals) * (pool_balance_fraction)
            token_staked = lptoken_data['reserves'][i] / (10**token_decimals) * (pool_staked_fraction)

            balances.append([token_address, token_balance, token_staked])
        
        if reward == True:
            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, pool_info = pool_info)
            
            result.append(balances)
            result.append(all_rewards)
       
        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return SushiSwapUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return SushiSwapUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return SushiSwapUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, reward = reward, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SushiSwapPoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def SushiSwapPoolBalances(lptoken_address, block, blockchain, **kwargs):
    
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

        for i in range(len(reserves)):
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

        return SushiSwapPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except GetNodeArchivalIndexError:
        index = 0

        return SushiSwapPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return SushiSwapPoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getWalletByTx
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'signature' = signature of the type of transaction that will be searched for
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getWalletByTx(lptoken_address, block, blockchain, **kwargs):

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
        signature = kwargs['signature']
    except:
        signature = 'deposit(uint256,uint256,address)'

    try:
        web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address) 
        
        if block == 'latest':
            block = lastBlock(blockchain, web3 = web3)
        
        chef_contract = getPoolInfo(web3, lptoken_address, block, blockchain)[0]

        if chef_contract != None:
        
            tx_hex_bytes = Web3.keccak(text = signature)[0:4].hex()

            block_start = block
            while True:

                block_start = block_start - 1000000
                
                lptoken_txs = getTokenTx(lptoken_address, chef_contract.address, block_start, block, blockchain)

                for lptoken_tx in lptoken_txs:
                    txs = getTxList(lptoken_tx['from'], block_start, block, blockchain)
                
                    for tx in txs:
                        
                        if tx['input'][0:10] == tx_hex_bytes:
                            return tx['from']
       
    except GetNodeLatestIndexError:
        index = 0

        return getWalletByTx(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except GetNodeArchivalIndexError:
        index = 0

        return getWalletByTx(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return getWalletByTx(lptoken_address, block, blockchain, index = index + 1, execution = execution)