from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# BALANCER VAULT
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Balancer Vault Contract Address
VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LIQUIDITY GAUGE FACTORY
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ethereum Liquidity Gauge Factory Contract Address
LIQUIDITY_GAUGE_FACTORY_ETHEREUM = '0x4E7bBd911cf1EFa442BC1b2e9Ea01ffE785412EC'

# Polygon Liquidity Gauge Factory Contract Address
LIQUIDITY_GAUGE_FACTORY_POLYGON = '0x3b8cA519122CdD8efb272b0D3085453404B25bD0'

# Arbitrum Liquidity Gauge Factory Contract Address
LIQUIDITY_GAUGE_FACTORY_ARBITRUM = '0xb08E16cFc07C684dAA2f93C70323BAdb2A6CBFd2'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# veBAL 
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# veBAL Contract Address
VEBAL = '0xC128a9954e6c874eA3d62ce62B468bA073093F25'

# veBAL Fee Distributor Contract
VEBAL_FEE_DISTRIBUTOR = '0x26743984e3357eFC59f2fd6C1aFDC310335a61c9'

# veBAL Reward Tokens - BAL, bb-a-USD
VEBAL_REWARD_TOKENS = [BAL_ETH, BB_A_USD_ETH]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Balancer Vault ABI - getPoolTokens
ABI_VAULT = '[{"inputs":[{"internalType":"bytes32","name":"poolId","type":"bytes32"}],"name":"getPoolTokens","outputs":[{"internalType":"contract IERC20[]","name":"tokens","type":"address[]"},{"internalType":"uint256[]","name":"balances","type":"uint256[]"},{"internalType":"uint256","name":"lastChangeBlock","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Liquidity Gauge Factory ABI - getPoolGauge
ABI_LIQUIDITY_GAUGE_FACTORY = '[{"inputs":[{"internalType":"address","name":"pool","type":"address"}],"name":"getPoolGauge","outputs":[{"internalType":"contract ILiquidityGauge","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

# veBAL ABI - locked, token
ABI_VEBAL = '[{"stateMutability":"view","type":"function","name":"token","inputs":[],"outputs":[{"name":"","type":"address"}]}, {"stateMutability":"view","type":"function","name":"locked","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"tuple","components":[{"name":"amount","type":"int128"},{"name":"end","type":"uint256"}]}]}]'

# veBAL Fee Distributor ABI - claimTokens
ABI_VEBAL_FEE_DISTRIBUTOR = '[{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"contract IERC20[]","name":"tokens","type":"address[]"}],"name":"claimTokens","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]'

# LP Token ABI - getPoolId, decimals, getVirtualSupply, totalSupply, getBptIndex, balanceOf
ABI_LPTOKEN = '[{"inputs":[],"name":"getPoolId","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getVirtualSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getBptIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

# Gauge ABI - claimable_tokens, claimable_reward, reward_count, reward_tokens
ABI_GAUGE = '[{"stateMutability":"nonpayable","type":"function","name":"claimable_tokens","inputs":[{"name":"addr","type":"address"}],"outputs":[{"name":"","type":"uint256"}]}, {"stateMutability":"view","type":"function","name":"claimable_reward","inputs":[{"name":"_user","type":"address"},{"name":"_reward_token","type":"address"}],"outputs":[{"name":"","type":"uint256"}]}, {"stateMutability":"view","type":"function","name":"reward_count","inputs":[],"outputs":[{"name":"","type":"uint256"}]}, {"stateMutability":"view","type":"function","name":"reward_tokens","inputs":[{"name":"arg0","type":"uint256"}],"outputs":[{"name":"","type":"address"}]}]'

# ABI - Pool Tokens - decimals, getRate
ABI_POOL_TOKENS_BALANCER = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"}, {"inputs":[],"name":"getRate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}, {"inputs":[],"name":"getMainToken","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getGaugeFactoryAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getGaugeFactoryAddress(blockchain):

    if blockchain == ETHEREUM:
        return LIQUIDITY_GAUGE_FACTORY_ETHEREUM
    
    elif blockchain == POLYGON:
        return LIQUIDITY_GAUGE_FACTORY_POLYGON
    
    elif blockchain == ARBITRUM:
        return LIQUIDITY_GAUGE_FACTORY_ARBITRUM

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPTokenData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPTokenData(web3, lptoken_address, gauge_address, wallet, block, blockchain):

    lptoken_data = {}

    lptoken_data['contract'] = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)
    lptoken_data['PoolId'] = lptoken_data['contract'].functions.getPoolId().call()
    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()

    try:
        lptoken_data['totalSupply'] = lptoken_data['contract'].functions.getVirtualSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])
        lptoken_data['isBoosted'] = True
    except:
        lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])
        lptoken_data['isBoosted'] = False

    if lptoken_data['isBoosted'] == True:
        lptoken_data['BptIndex'] = lptoken_data['contract'].functions.getBptIndex().call()
    else:
        lptoken_data['BptIndex'] = None

    lptoken_data['balanceOf'] = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    if gauge_address != ZERO_ADDRESS:
        lptoken_data['staked'] = balanceOf(wallet, gauge_address, block, blockchain, web3 = web3)
    else:
        lptoken_data['staked'] = 0

    lptoken_data['locked'] = 0
    if blockchain == ETHEREUM:
        vebal_contract = getContract(VEBAL, blockchain, web3 = web3, abi = ABI_VEBAL, block = block)

        if (lptoken_address == vebal_contract.functions.token().call()):
            try:
                lptoken_data['locked'] = vebal_contract.functions.locked(wallet).call(block_identifier = block)[0] / (10**lptoken_data['decimals'])
            except:
                lptoken_data['locked'] = 0

    return lptoken_data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getBALAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getBALAddress(blockchain):

    if blockchain == ETHEREUM:
        return BAL_ETH
    elif blockchain == POLYGON:
        return BAL_POL

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getBALRewards
# Output:
# 1 - Tuples: [bal_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getBALRewards(web3, gauge_contract, wallet, block, blockchain):

    bal_address = getBALAddress(blockchain)
    bal_decimals = getDecimals(bal_address, blockchain, web3 = web3)

    if blockchain == ETHEREUM:
        bal_rewards = gauge_contract.functions.claimable_tokens(wallet).call(block_identifier = block) / (10**bal_decimals)
    else:
        bal_rewards = gauge_contract.functions.claimable_reward(wallet, bal_address).call(block_identifier = block) / (10**bal_decimals)

    return [bal_address, bal_rewards]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getRewards
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getRewards(web3, gauge_contract, wallet, block, blockchain):

    rewards = []

    for i in range(gauge_contract.functions.reward_count().call()):

        token_address = gauge_contract.functions.reward_tokens(i).call()
        token_rewards = gauge_contract.functions.claimable_reward(wallet, token_address).call(block_identifier = block)

        token_decimals = getDecimals(token_address, blockchain, web3 = web3)
        token_rewards = token_rewards / (10**token_decimals)

        rewards.append([token_address, token_rewards])

    return rewards

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getVEBALRewards
# Output:
# 1 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getVEBALRewards(web3, wallet, block, blockchain):

    vebal_rewards = []

    fee_distributor_contract = getContract(VEBAL_FEE_DISTRIBUTOR, blockchain, web3 = web3, abi = ABI_VEBAL_FEE_DISTRIBUTOR, block = block)
    claim_tokens = fee_distributor_contract.functions.claimTokens(wallet, VEBAL_REWARD_TOKENS).call(block_identifier = block)

    for i in range(len(VEBAL_REWARD_TOKENS)):
        token_address = VEBAL_REWARD_TOKENS[i]
        token_rewards = claim_tokens[i]
        
        token_decimals = getDecimals(token_address, blockchain, web3 = web3)
        token_rewards = token_rewards / (10**token_decimals)

        vebal_rewards.append([token_address, token_rewards])

    return vebal_rewards

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getAllRewards
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'gauge_address' = gauge_address -> Improves performance
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
            gauge_address = kwargs['gauge_address']
        except:
            gauge_factory_address = getGaugeFactoryAddress(blockchain)
            gauge_factory_contract = getContract(gauge_factory_address, blockchain, web3 = web3, abi = ABI_LIQUIDITY_GAUGE_FACTORY, block = block)
            gauge_address = gauge_factory_contract.functions.getPoolGauge(lptoken_address).call()
        
        # veBAL Rewards
        if blockchain == ETHEREUM:
            vebal_contract = getContract(VEBAL, blockchain, web3 = web3, abi = ABI_VEBAL, block = block)

            if (lptoken_address == vebal_contract.functions.token().call()):
                vebal_rewards = getVEBALRewards(web3, wallet, block, blockchain)

                if len(vebal_rewards) > 0:
                    for vebal_reward in vebal_rewards:
                        all_rewards.append(vebal_reward)

        if gauge_address != ZERO_ADDRESS:
            gauge_contract = getContract(gauge_address, blockchain, web3 = web3, abi = ABI_GAUGE, block = block)

            bal_rewards = getBALRewards(web3, gauge_contract, wallet, block, blockchain)
            all_rewards.append(bal_rewards)

            rewards = getRewards(web3, gauge_contract, wallet, block, blockchain)

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
# BalancerUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance, locked_balance]
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def BalancerUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

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
        aura_staked = kwargs['aura_staked']
    except:
        aura_staked = None

    try:
        web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)

        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)

        vault_contract = getContract(VAULT, blockchain, web3 = web3, abi = ABI_VAULT, block = block)
        
        gauge_factory_address = getGaugeFactoryAddress(blockchain)
        gauge_factory_contract = getContract(gauge_factory_address, blockchain, web3 = web3, abi = ABI_LIQUIDITY_GAUGE_FACTORY, block = block)

        gauge_address = gauge_factory_contract.functions.getPoolGauge(lptoken_address).call()

        lptoken_data = getLPTokenData(web3, lptoken_address, gauge_address, wallet, block, blockchain)

        pool_tokens_data = vault_contract.functions.getPoolTokens(lptoken_data['PoolId']).call(block_identifier = block)
        pool_tokens = pool_tokens_data[0]
        pool_balances = pool_tokens_data[1]

        pool_balance_fraction = lptoken_data['balanceOf'] / lptoken_data['totalSupply']
        pool_staked_fraction = lptoken_data['staked'] / lptoken_data['totalSupply']
        pool_locked_fraction = lptoken_data['locked'] / lptoken_data['totalSupply']

        for i in range(len(pool_tokens)):

            if i == lptoken_data['BptIndex']:
                continue

            token_address = pool_tokens[i]
            token_contract = getContract(token_address, blockchain, web3 = web3, abi = ABI_POOL_TOKENS_BALANCER, block = block)

            token_decimals = token_contract.functions.decimals().call()

            if lptoken_data['isBoosted'] == True:
                token_rate = token_contract.functions.getRate().call(block_identifier = block) / (10**token_decimals)
            else:
                token_rate = 1

            token_balance = pool_balances[i] / (10**token_decimals) * pool_balance_fraction * token_rate

            if aura_staked == None:
                token_staked = pool_balances[i] / (10**token_decimals) * pool_staked_fraction * token_rate
            else:
                aura_pool_fraction = aura_staked / lptoken_data['totalSupply']
                token_staked = pool_balances[i] / (10**token_decimals) * aura_pool_fraction

            token_locked = pool_balances[i] / (10**token_decimals) * pool_locked_fraction * token_rate

            if lptoken_data['isBoosted'] == True:
                balances.append([token_contract.functions.getMainToken().call(), token_balance, token_staked, token_locked])
            else:
                balances.append([pool_tokens[i], token_balance, token_staked, token_locked])

        if reward == True:
            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, gauge_address = gauge_address)

            result.append(balances)
            result.append(all_rewards)

        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return BalancerUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return BalancerUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return BalancerUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, reward = reward, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# BalancerPoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def BalancerPoolBalances(lptoken_address, block, blockchain, **kwargs):

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

        vault_contract = getContract(VAULT, blockchain, web3 = web3, abi = ABI_VAULT, block = block)

        lptoken_data = getLPTokenData(web3, lptoken_address, ZERO_ADDRESS, ZERO_ADDRESS, block, blockchain)

        pool_tokens_data = vault_contract.functions.getPoolTokens(lptoken_data['PoolId']).call(block_identifier = block)
        pool_tokens = pool_tokens_data[0]
        pool_balances = pool_tokens_data[1]

        for i in range(len(pool_tokens)):

            if i == lptoken_data['BptIndex']:
                continue

            token_address = pool_tokens[i]
            token_contract = getContract(token_address, blockchain, web3 = web3, abi = ABI_POOL_TOKENS_BALANCER, block = block)

            token_decimals = token_contract.functions.decimals().call()

            if lptoken_data['isBoosted'] == True:
                token_rate = token_contract.functions.getRate().call(block_identifier = block) / (10**token_decimals)
            else:
                token_rate = 1

            token_balance = pool_balances[i] / (10**token_decimals) * token_rate

            if lptoken_data['isBoosted'] == True:
                balances.append([token_contract.functions.getMainToken().call(), token_balance])
            else:
                balances.append([pool_tokens[i], token_balance])

        return balances
    
    except GetNodeLatestIndexError:
        index = 0

        return BalancerPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return BalancerPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return BalancerPoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)