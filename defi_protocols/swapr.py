from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# STAKING REWARDS CONTRACT ADDRESSES
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETHEREUM
SRC_ETHEREUM = '0x156F0568a6cE827e5d39F6768A5D24B694e1EA7b'

# XDAI
SRC_XDAI = '0xa039793Af0bb060c597362E8155a0327d9b8BEE8'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Staking Rewards Contract ABI - distributions, getDistributionsAmount
ABI_SRC = '[{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"distributions","outputs":[{"internalType":"contract IERC20StakingRewardsDistribution","name":"","type":"address"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getDistributionsAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Distribution ABI - stakableToken, stakers, getRewardTokens, claimableRewards
ABI_DISTRIBUTION = '[{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract IERC20"}],"name":"stakableToken","inputs":[]}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"stake","internalType":"uint256"}],"name":"stakers","inputs":[{"type":"address","name":"","internalType":"address"}]}, {"type":"function","stateMutability":"view","outputs":[{"type":"address[]","name":"","internalType":"address[]"}],"name":"getRewardTokens","inputs":[]}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256[]","name":"","internalType":"uint256[]"}],"name":"claimableRewards","inputs":[{"type":"address","name":"_account","internalType":"address"}]}]'

# LP Token ABI - decimals, totalSupply, getReserves, balanceOf, token0, token1
ABI_LPTOKEN = '[{"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint8","name":"","internalType":"uint8"}],"name":"decimals","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalSupply","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint112","name":"_reserve0","internalType":"uint112"},{"type":"uint112","name":"_reserve1","internalType":"uint112"},{"type":"uint32","name":"_blockTimestampLast","internalType":"uint32"}],"name":"getReserves","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"balanceOf","inputs":[{"type":"address","name":"","internalType":"address"}],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"address"}],"name":"token0","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"address"}],"name":"token1","inputs":[],"constant":true}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getStakingRewardsContract
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getStakingRewardsContract(web3, block, blockchain):

    if blockchain == ETHEREUM:
        staking_rewards_contract = getContract(SRC_ETHEREUM, blockchain, web3 = web3, abi = ABI_SRC, block = block)
    
    elif blockchain == XDAI:
        staking_rewards_contract = getContract(SRC_XDAI, blockchain, web3 = web3, abi = ABI_SRC, block = block)
    
    return staking_rewards_contract

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getDistributionContracts
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getDistributionContracts(web3, lptoken_address, staking_rewards_contract, campaigns, block, blockchain):

    distribution_contracts = []

    if campaigns != 0:
        campaign_counter = 0
        
        distributions_amount = staking_rewards_contract.functions.getDistributionsAmount().call()

        for i in range(distributions_amount):
            distribution_address = staking_rewards_contract.functions.distributions(distributions_amount - (i + 1)).call()
            distribution_contract = getContract(distribution_address, blockchain, web3 = web3, abi = ABI_DISTRIBUTION, block = block)
            stakable_token = web3.toChecksumAddress(distribution_contract.functions.stakableToken().call())

            if stakable_token == lptoken_address:
                distribution_contracts.append(distribution_contract)
                campaign_counter += 1
                
                if campaigns == 'all' or campaign_counter < campaigns:               
                    continue
                else:
                    break
    
    return distribution_contracts

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPTokenData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPTokenData(web3, lptoken_address, distribution_contracts, wallet, block, blockchain):

    lptoken_data = {}
     
    lptoken_data['contract'] = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)
    
    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()
    lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])
    lptoken_data['reserves'] = lptoken_data['contract'].functions.getReserves().call(block_identifier = block)

    lptoken_data['staked'] = 0
    if distribution_contracts != []:
        for distribution_contract in distribution_contracts:
            lptoken_data['staked'] += distribution_contract.functions.stakers(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    lptoken_data['balanceOf'] = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    return lptoken_data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'distribution_contracts' -> Improves performance
# 'campaigns' = number of campaigns from which the data is retrieved / 
# 'campaigns' = 0 it does not search for any campaign nor distribution contract 
# 'campaigns' = 'all' retrieves the data from all campaigns
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getAllRewards(wallet, lptoken_address, block, blockchain, **kwargs):

    all_rewards = []
    rewards = {}

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
        campaigns = kwargs['campaigns']
    except:
        campaigns = 1
    
    try:
        if web3 == None: 
            web3 = getNode(blockchain, block = block, index = index)

        try:
            distribution_contracts = kwargs['distribution_contracts']
        except:
            staking_rewards_contract = getStakingRewardsContract(web3, block, blockchain)
            distribution_contracts = getDistributionContracts(web3, lptoken_address, staking_rewards_contract, campaigns, block, blockchain)

        if distribution_contracts == []:
            return []
        
        else:
            for distribution_contract in distribution_contracts:
                reward_tokens = distribution_contract.functions.getRewardTokens().call()
                claimable_rewards = distribution_contract.functions.claimableRewards(wallet).call(block_identifier = block)

                for i in range(len(reward_tokens)):
                    reward_token_decimals = getDecimals(reward_tokens[i], blockchain, web3 = web3)
                    reward_token_amount = claimable_rewards[i] / (10**reward_token_decimals)

                    try:
                        rewards[reward_tokens[i]] += reward_token_amount
                    except:
                        rewards[reward_tokens[i]] = reward_token_amount

            for key in rewards.keys():
                all_rewards.append([key, rewards[key]])

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
# SwaprUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'campaigns' = number of campaigns from which the data is retrieved / 
# 'campaigns' = 0 it does not search for any campaign nor distribution contract 
# 'campaigns' = 'all' retrieves the data from all campaigns
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance]
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def SwaprUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

    result = []
    balances = []
    distribution_contracts = []

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
        campaigns = kwargs['campaigns']
    except:
        campaigns = 1

    try:
        web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)

        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)

        staking_rewards_contract = getStakingRewardsContract(web3, block, blockchain)
        distribution_contracts = getDistributionContracts(web3, lptoken_address, staking_rewards_contract, campaigns, block, blockchain)

        lptoken_data = getLPTokenData(web3, lptoken_address, distribution_contracts, wallet, block, blockchain)

        pool_balance_fraction = lptoken_data['balanceOf'] / lptoken_data['totalSupply']
        pool_staked_fraction = lptoken_data['staked'] / lptoken_data['totalSupply']

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
            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, distribution_contracts = distribution_contracts)

            result.append(balances)
            result.append(all_rewards)

        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return SwaprUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return SwaprUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return SwaprUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, reward = reward, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SwaprPoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def SwaprPoolBalances(lptoken_address, block, blockchain, **kwargs):

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

            token_balance = reserves[i] / (10**token_decimals)

            balances.append([token_address, token_balance])

        return balances
    
    except GetNodeLatestIndexError:
        index = 0

        return SwaprPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return SwaprPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return SwaprPoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)
