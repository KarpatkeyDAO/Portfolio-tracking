from defi_protocols.balancer import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# BOOSTER
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Booster (Main Deposit Contract) Address
BOOSTER = '0x7818A1DA7BD1E64c199029E86Ba244a9798eEE10'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Booster ABI - poolInfo
ABI_BOOSTER = '[{"inputs":[],"name":"poolLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"poolInfo","outputs":[{"internalType":"address","name":"lptoken","type":"address"},{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"gauge","type":"address"},{"internalType":"address","name":"crvRewards","type":"address"},{"internalType":"address","name":"stash","type":"address"},{"internalType":"bool","name":"shutdown","type":"bool"}],"stateMutability":"view","type":"function"}]'

# Rewards ABI - balanceOf, totalSupply, earned, rewardToken, extraRewardsLength, extraRewards
ABI_REWARDS = '[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"earned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"rewardToken","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"extraRewardsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"extraRewards","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

# AURA ABI - EMISSIONS_MAX_SUPPLY, INIT_MINT_AMOUNT, decimals, reductionPerCliff, totalCliffs, totalSupply
ABI_AURA = '[{"inputs":[],"name":"EMISSIONS_MAX_SUPPLY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"INIT_MINT_AMOUNT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"reductionPerCliff","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalCliffs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getBALRewards
# Output:
# 1 - Tuples: [bal_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getBALRewards(web3, bal_rewards_contract, wallet, block, blockchain):
    
    reward_token_address = bal_rewards_contract.functions.rewardToken().call()
    reward_token_decimals = getDecimals(reward_token_address, blockchain, web3 = web3)
    bal_rewards = bal_rewards_contract.functions.earned(wallet).call(block_identifier = block) / (10**reward_token_decimals)

    return [reward_token_address, bal_rewards]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getExtraRewards
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getExtraRewards(web3, bal_rewards_contract, wallet, block, blockchain):
    
    extra_rewards = []

    extra_rewards_length = bal_rewards_contract.functions.extraRewardsLength().call(block_identifier = block)

    for i in range(extra_rewards_length):
        
        extra_reward_contract_address = bal_rewards_contract.functions.extraRewards(i).call(block_identifier = block)
        extra_reward_contract = getContract(extra_reward_contract_address, blockchain, web3 = web3, abi = ABI_REWARDS, block = block)

        extra_reward_token_address = extra_reward_contract.functions.rewardToken().call()
        extra_reward_token_decimals = getDecimals(extra_reward_token_address, blockchain, web3 = web3)

        extra_reward = extra_reward_contract.functions.earned(wallet).call(block_identifier = block) / (10**extra_reward_token_decimals)

        extra_rewards.append([extra_reward_token_address, extra_reward])
    
    return extra_rewards

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAURAMintAmount
# Output:
# 1 - Tuple: [aura_token_address, minted_amount]
# WARNING: Check the amount of AURA retrieved
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getAURAMintAmount(web3, bal_earned, block, blockchain):

    aura_amount = 0

    aura_contract = getContract(AURA_ETH, blockchain, web3 = web3, abi = ABI_AURA, block = block)

    aura_total_supply = aura_contract.functions.totalSupply().call(block_identifier = block)
    init_mint_amount = aura_contract.functions.INIT_MINT_AMOUNT().call(block_identifier = block)
    reduction_per_cliff = aura_contract.functions.reductionPerCliff().call(block_identifier = block)

    emissions_minted = aura_total_supply - init_mint_amount
    cliff = emissions_minted / reduction_per_cliff

    total_cliffs = aura_contract.functions.totalCliffs().call(block_identifier = block)

    if cliff < total_cliffs:

        reduction = ((total_cliffs - cliff) * 2.5) + 700

        aura_amount = (bal_earned * reduction) / total_cliffs

        amount_till_max = aura_contract.functions.EMISSIONS_MAX_SUPPLY().call(block_identifier = block) - emissions_minted
        
        if aura_amount > amount_till_max:
            aura_amount = amount_till_max
    
    return [AURA_ETH, aura_amount]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'bal_rewards_contract' = bal_rewards_contract -> Improves performance
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
            bal_rewards_contract = kwargs['bal_rewards_contract']
        except:
            booster_contract = getContract(BOOSTER, blockchain, web3 = web3, abi = ABI_BOOSTER, block = block)
            pool_info = getPoolInfo(booster_contract, lptoken_address, block)

            if pool_info == None:
                print('Error: Incorrect Convex LPToken Address: ', lptoken_address)
                return None

            bal_rewards_address = pool_info[3]
            bal_rewards_contract = getContract(bal_rewards_address, blockchain, web3 = web3, abi = ABI_REWARDS, block = block)    
        
        bal_rewards = getBALRewards(web3, bal_rewards_contract, wallet, block, blockchain)
        all_rewards.append(bal_rewards)
        
        # all_rewards[0][1] = bal_rewards_amount - aura_mint_amount is calculated using the bal_rewards_amount
        if all_rewards[0][1] >= 0:
            aura_mint_amount = getAURAMintAmount(web3, all_rewards[0][1], block, blockchain)
        
            if (len(aura_mint_amount) > 0):
                all_rewards.append(aura_mint_amount)

        extra_rewards = getExtraRewards(web3, bal_rewards_contract, wallet, block, blockchain)
        
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
# getPoolInfo - Retrieves the result of the pool_info method if there is a match for the lptoken_address - Otherwise it returns None
# Output: pool_info method return a list with the following data: 
# [0] lptoken address, [1] token address, [2] gauge address, [3] crvRewards address, [4] stash adress, [5] shutdown bool
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPoolInfo(booster_contract, lptoken_address, block):

    number_of_pools = booster_contract.functions.poolLength().call(block_identifier = block)

    for pool_id in range(number_of_pools):

        pool_info = booster_contract.functions.poolInfo(pool_id).call(block_identifier = block)
        address = pool_info[0]

        if address == lptoken_address:
            return pool_info

    return None

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# AuraUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'no_balancer_underlying' = True -> retrieves the LP Token balance / 
# 'no_balancer_underlying' = False or not passed onto the function -> retrieves the balance of the underlying Balancer tokens
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance] | [liquidity_token_address, staked_balance] -> depending on 'no_balancer_underlying' value 
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def AuraUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

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
        no_balancer_underlying = kwargs['no_balancer_underlying']
    except:
        no_balancer_underlying = False

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

        pool_info = getPoolInfo(booster_contract, lptoken_address, block)

        if pool_info == None:
            print('Error: Incorrect Aura LPToken Address: ', lptoken_address)
            return None
        
        bal_rewards_address = pool_info[3]
        bal_rewards_contract = getContract(bal_rewards_address, blockchain, web3 = web3, abi = ABI_REWARDS, block = block)
        
        # poolTokenAddress = pool_info[1]
        pool_token_decimals = getDecimals(lptoken_address, blockchain, web3 = web3)
        pool_token_staked = bal_rewards_contract.functions.balanceOf(wallet).call(block_identifier = block) / (10**pool_token_decimals)

        if no_balancer_underlying == False:
            balancer_data = BalancerUnderlying(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, aura_staked = pool_token_staked)
            balances = [[balancer_data[i][0], balancer_data[i][2]] for i in range(len(balancer_data))]
        else:
            balances.append([lptoken_address, pool_token_staked])

        if reward == True:
            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, bal_rewards_contract = bal_rewards_contract)
            
            result.append(balances)
            result.append(all_rewards)
        
        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return AuraUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return AuraUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return AuraUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, reward = reward, execution = execution)