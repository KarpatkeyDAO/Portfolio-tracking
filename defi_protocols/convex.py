from defi_protocols.curve import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# BACKLOG LIST
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Rewards when you stake CVX

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# BOOSTER
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Booster (Main Deposit Contract) Address
BOOSTER = '0xF403C135812408BFbE8713b5A23a04b3D48AAE31'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Booster ABI - poolInfo
ABI_BOOSTER = '[{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"poolInfo","outputs":[{"internalType":"address","name":"lptoken","type":"address"},{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"gauge","type":"address"},{"internalType":"address","name":"crvRewards","type":"address"},{"internalType":"address","name":"stash","type":"address"},{"internalType":"bool","name":"shutdown","type":"bool"}],"stateMutability":"view","type":"function"}]'

# Rewards ABI - balanceOf, totalSupply, earned, rewardToken, extraRewardsLength, extraRewards
ABI_REWARDS = '[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"earned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"rewardToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"extraRewardsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"extraRewards","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

# CVX ABI - reductionPerCliff, totalCliffs, maxSupply, totalSupply
ABI_CVX = '[{"inputs":[],"name":"reductionPerCliff","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalCliffs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"maxSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPoolInfo - Retrieves the result of the pool_info method if there is a match for the lptoken_address - Otherwise it returns None
# Output: pool_info method return a list with the following data: 
# [0] lptoken address, [1] token address, [2] gauge address, [3] crvRewards address, [4] stash adress, [5] shutdown bool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPoolInfo(booster_contract, lptoken_address):

    with open('../db/convex.json', 'r') as db_file:
        # Reading from json file
        db_data = json.load(db_file)
    
    try:
        pool_info = db_data['pools'][lptoken_address]
        return [lptoken_address, pool_info['token'], pool_info['gauge'], pool_info['crvRewards']]
    
    except:
        return None

    # address = None
    # pool_id = -1

    # while address != lptoken_address:

    #     pool_id = pool_id + 1

    #     try:
    #         pool_info = booster_contract.functions.poolInfo(pool_id).call()
    #         address = pool_info[0]
            
    #         if address == lptoken_address:
    #             return pool_info
        
    #     except:
    #         return None

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getCRVRewards
# Output:
# 1 - Tuples: [crv_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getCRVRewards(web3, crv_rewards_contract, wallet, block, blockchain):
    
    reward_token_address = crv_rewards_contract.functions.rewardToken().call()
    reward_token_decimals = getDecimals(reward_token_address, blockchain, web3 = web3)
    crv_rewards = crv_rewards_contract.functions.earned(wallet).call(block_identifier = block) / (10**reward_token_decimals)

    return [reward_token_address, crv_rewards]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getExtraRewards
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getExtraRewards(web3, crv_rewards_contract, wallet, block, blockchain):
    
    extra_rewards = []

    extra_rewards_length = crv_rewards_contract.functions.extraRewardsLength().call(block_identifier = block)

    for i in range(extra_rewards_length):
        
        extra_reward_contract_address = crv_rewards_contract.functions.extraRewards(i).call(block_identifier = block)
        extra_reward_contract = getContract(extra_reward_contract_address, blockchain, web3 = web3, abi = ABI_REWARDS, block = block)

        extra_reward_token_address = extra_reward_contract.functions.rewardToken().call()
        extra_reward_token_decimals = getDecimals(extra_reward_token_address, blockchain, web3 = web3)

        extra_reward = extra_reward_contract.functions.earned(wallet).call(block_identifier = block) / (10**extra_reward_token_decimals)

        extra_rewards.append([extra_reward_token_address, extra_reward])
    
    return extra_rewards

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getCVXMintAmount
# Output:
# 1 - Tuple: [cvx_token_address, minted_amount]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getCVXMintAmount(web3, crv_earned, block, blockchain):

    cvx_contract = getContract(CVX_ETH, blockchain, web3 = web3, abi = ABI_CVX, block = block)

    cliff_size = cvx_contract.functions.reductionPerCliff().call(block_identifier = block)
    cliff_count = cvx_contract.functions.totalCliffs().call(block_identifier = block)
    max_supply = cvx_contract.functions.maxSupply().call(block_identifier = block)

    cvx_total_supply = cvx_contract.functions.totalSupply().call(block_identifier = block)

    current_cliff = cvx_total_supply / cliff_size

    if(current_cliff < cliff_count ):

        remaining = cliff_count - current_cliff
        cvx_earned = crv_earned * remaining / cliff_count
        amount_till_max = max_supply - cvx_total_supply

        if(cvx_earned > amount_till_max):
            cvx_earned = amount_till_max
    
    return [CVX_ETH, cvx_earned]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'crv_rewards_contract' = crv_rewards_contract -> Improves performance
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
            crv_rewards_contract = kwargs['crv_rewards_contract']
        except:
            booster_contract = getContract(BOOSTER, blockchain, web3 = web3, abi = ABI_BOOSTER, block = block)
            pool_info = getPoolInfo(booster_contract, lptoken_address)

            if pool_info == None:
                print('Error: Incorrect Convex LPToken Address: ', lptoken_address)
                return None

            crv_rewards_address = pool_info[3]
            crv_rewards_contract = getContract(crv_rewards_address, blockchain, web3 = web3, abi = ABI_REWARDS, block = block)    
        
        crv_rewards = getCRVRewards(web3, crv_rewards_contract, wallet, block, blockchain)
        all_rewards.append(crv_rewards)
        
        # all_rewards[0][1] = crv_rewards_amount - cvx_mint_amount is calculated using the crv_rewards_amount
        if all_rewards[0][1] >= 0:
            cvx_mint_amount = getCVXMintAmount(web3, all_rewards[0][1], block, blockchain)
        
            if (len(cvx_mint_amount) > 0):
                all_rewards.append(cvx_mint_amount)

        extra_rewards = getExtraRewards(web3, crv_rewards_contract, wallet, block, blockchain)
        
        if len(extra_rewards) > 0:
            for extra_reward in extra_rewards:
                all_rewards.append(extra_reward)

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
# ConvexUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'no_curve_underlying' = True -> retrieves the LP Token balance / 
# 'no_curve_underlying' = False or not passed onto the function -> retrieves the balance of the underlying Curve tokens
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance] | [liquidity_token_address, staked_balance] -> depending on 'no_curve_underlying' value 
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ConvexUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

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
        no_curve_underlying = kwargs['no_curve_underlying']
    except:
        no_curve_underlying = False

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
        
        booster_contract = getContract(BOOSTER, blockchain, web3 = web3, abi = ABI_BOOSTER, block = block)

        pool_info = getPoolInfo(booster_contract, lptoken_address)

        if pool_info == None:
            print('Error: Incorrect Convex LPToken Address: ', lptoken_address)
            return None
        
        crv_rewards_address = pool_info[3]
        crv_rewards_contract = getContract(crv_rewards_address, blockchain, web3 = web3, abi = ABI_REWARDS, block = block)
        
        # poolTokenAddress = pool_info[1]
        pool_token_decimals = getDecimals(lptoken_address, blockchain, web3 = web3)
        pool_token_staked = crv_rewards_contract.functions.balanceOf(wallet).call(block_identifier = block) / (10**pool_token_decimals)

        if no_curve_underlying == False:
            balances = CurveUnderlying(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, convex_staked = pool_token_staked)       
        else:
            balances.append([lptoken_address, pool_token_staked])

        if reward == True:
            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, crv_rewards_contract = crv_rewards_contract)
            
            result.append(balances)
            result.append(all_rewards)
        
        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return ConvexUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return ConvexUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return ConvexUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, reward = reward, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ConvexPoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'no_curve_underlying' = True -> retrieves the LP Token balance / 
# 'no_curve_underlying' = False or not passed onto the function -> retrieves the balance of the underlying Curve tokens
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance] | [liquidity_token_address, staked_balance] -> depending on 'no_curve_underlying' value 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ConvexPoolBalances(lptoken_address, block, blockchain, **kwargs):

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

        balances = CurvePoolBalances(lptoken_address, block, blockchain, web3 = web3, index = index)

        return balances
    
    except GetNodeLatestIndexError:
        index = 0

        return ConvexPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return ConvexPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return ConvexPoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)