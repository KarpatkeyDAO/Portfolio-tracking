from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PROVIDER ADDRESS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
PROVIDER_ADDRESS = '0x0000000022D53366457F9d5E68Ec105046FC4383'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# POOL & GAUGE ADDRESSES
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ETHEREUM
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Curve.fi RAI3CRV
RAI3CRV_ADDRESS = '0x618788357D0EBd8A37e763ADab3bc575D54c2C7d'
# RAI3CRV_GAUGE_ADDRESS = ¿?

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# POLYGON
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# XDAI
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Curve.fi wxDAI/USDC/USDT
X3CRV_ADDRESS = '0x7f90122BF0700F9E7e1F688fe926940E8839F353'
X3CRV_GAUGE_ADDRESS = '0x78CF256256C8089d68Cde634Cf7cDEFb39286470'
X3CRV_GAUGE_ADDRESS_V2 ='0xB721Cc32160Ab0da2614CC6aB16eD822Aeebc101'

# Curve.fi sGNO/GNO
SGNO_GNO_ADDRESS = '0xBdF4488Dcf7165788D438b62B4C8A333879B7078'
# SGNO_GNO_GAUGE_ADDRESS = ¿?

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Provider ABI - get_address
ABI_PROVIDER = '[{"name":"get_address","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":"_id"}],"stateMutability":"view","type":"function","gas":1308}]'

# Registry for Regular Pools ABI - get_gauges, get_pool_from_lp_token
ABI_REGISTRY_REGULAR_POOLS = '[{"type":"function","stateMutability":"view","outputs":[{"type":"address[10]","name":""},{"type":"int128[10]","name":""}],"name":"get_gauges","inputs":[{"type":"address","name":"_pool"}],"gas":28534}, {"stateMutability":"view","type":"function","name":"get_pool_from_lp_token","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"address"}],"gas":2443}]'

# Registry for Factory Pools ABI - get_gauge
ABI_REGISTRY_FACTORY_POOLS = '[{"stateMutability":"view","type":"function","name":"get_gauge","inputs":[{"name":"_pool","type":"address"}],"outputs":[{"name":"","type":"address"}],"gas":3089}]'

# Registry for V2 Pools ABI - get_gauges, get_pool_from_lp_token
ABI_REGISTRY_V2_POOLS = '[{"stateMutability":"view","type":"function","name":"get_gauges","inputs":[{"name":"_pool","type":"address"}],"outputs":[{"name":"","type":"address[10]"},{"name":"","type":"int128[10]"}],"gas":26055}, {"stateMutability":"view","type":"function","name":"get_pool_from_lp_token","inputs":[{"name":"arg0","type":"address"}],"outputs":[{"name":"","type":"address"}],"gas":3548}]'

# LP Token ABI - decimals, totalSupply, minter, balanceOf
ABI_LPTOKEN = '[{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":""}],"name":"decimals","inputs":[],"gas":288}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":""}],"name":"totalSupply","inputs":[],"gas":2808}, {"type":"function","stateMutability":"view","outputs":[{"type":"address","name":""}],"name":"minter","inputs":[],"gas":2838}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":""}],"name":"balanceOf","inputs":[{"type":"address","name":"arg0"}],"gas":2963}]'

# Pool ABI - coins, balances
ABI_POOL = '[{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":""}],"name":"coins","inputs":[{"type":"uint256","name":"arg0"}],"gas":1917}, {"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":""}],"name":"balances","inputs":[{"type":"uint256","name":"arg0"}],"gas":1947}]'

# Gauge ABI - crv_token, claimable_tokens, rewarded_token, claimable_reward, claimed_rewards_for, reward_tokens, claimable_reward, claimable_reward_write
ABI_GAUGE = '[{"name":"crv_token","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":1451}, {"name":"claimable_tokens","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"addr"}],"stateMutability":"nonpayable","type":"function","gas":1989612}, {"name":"rewarded_token","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function","gas":2201}, {"name":"claimable_reward","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"addr"}],"stateMutability":"view","type":"function","gas":7300}, {"name":"claimed_rewards_for","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"arg0"}],"stateMutability":"view","type":"function","gas":2475}, {"name":"reward_tokens","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":"arg0"}],"stateMutability":"view","type":"function","gas":2550}, {"name":"claimable_reward","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":"_addr"},{"type":"address","name":"_token"}],"stateMutability":"nonpayable","type":"function","gas":1017930}, {"stateMutability":"nonpayable","type":"function","name":"claimable_reward_write","inputs":[{"name":"_addr","type":"address"},{"name":"_token","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"gas":1211002}]'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getRegistryContract
# id = 0 -> Registry for Regular Pools
# id = 3 -> Registry for Factory Pools
# id = 5 -> Registry for V2 Pools
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getRegistryContract(web3, id, block, blockchain):

    provider_contract = getContract(PROVIDER_ADDRESS, blockchain, web3 = web3, abi = ABI_PROVIDER, block = block)

    registry_address = provider_contract.functions.get_address(id).call()

    if id == 0:
        abi = ABI_REGISTRY_REGULAR_POOLS
    elif id == 3:
        abi = ABI_REGISTRY_FACTORY_POOLS
    elif id == 5:
        abi = ABI_REGISTRY_V2_POOLS
    else:
        abi = ABI_REGISTRY_REGULAR_POOLS

    return getContract(registry_address, blockchain, web3 = web3, abi = abi, block = block)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPoolGaugeAddress
# Output: gauge_address
# Order in which Gauges should be searched for:
# 1- Using the function get_gauges(address) from the Registry Contract
# 2- If the function retrieves the ZERO_ADDRESS this could indicate 1 of 2 things:
#   A- The gauge was not registered when the pool was created
#   B- The pool does not have an associated gauge
# IMPORTANT: to verify "A" -> always search in the documentation (section "Deployment Addresses, "https://curve.readthedocs.io/ref-addresses.html) 
#                             if the pool has an associated gauge
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPoolGaugeAddress(web3, pool_address, block, blockchain):

    # 1: Try to retrieve the gauge address assuming the pool is a Regular Pool
    registry_contract = getRegistryContract(web3, 0, block, blockchain)
    
    if registry_contract.address != ZERO_ADDRESS:
        gauge_address = registry_contract.functions.get_gauges(pool_address).call()[0][0]

    # 2: Try to retrieve the gauge address assuming the pool is a Factory Pool
    if gauge_address == ZERO_ADDRESS:
        registry_contract = getRegistryContract(web3, 3, block, blockchain)
        
        if registry_contract.address != ZERO_ADDRESS:
            gauge_address = registry_contract.functions.get_gauge(pool_address).call()
    
    # 3: Try to retrieve the gauge address assuming the pool is a V2 Pool
    if gauge_address == ZERO_ADDRESS:
        registry_contract = getRegistryContract(web3, 5, block, blockchain)

        if registry_contract.address != ZERO_ADDRESS:
            gauge_address = registry_contract.functions.get_gauges(pool_address).call()[0][0]

    # Pools which don't have their gauge registered in non of the registries
    if gauge_address == ZERO_ADDRESS:
        
        if pool_address == X3CRV_ADDRESS:
            gauge_address = X3CRV_GAUGE_ADDRESS
           
        else:
            gauge_address = None
    
    return gauge_address

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getPoolAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getPoolAddress(web3, lptoken_address, block, blockchain):

    # 1: Try to retrieve the pool address assuming the pool is a Regular Pool
    registry_contract = getRegistryContract(web3, 0, block, blockchain)
    
    if registry_contract.address != ZERO_ADDRESS:
        pool_address = registry_contract.functions.get_pool_from_lp_token(lptoken_address).call()
    
    # 2: Try to retrieve the pool address assuming the pool is a V2 Pool
    if pool_address == ZERO_ADDRESS:
        registry_contract = getRegistryContract(web3, 5, block, blockchain)

        if registry_contract.address != ZERO_ADDRESS:
            pool_address = registry_contract.functions.get_pool_from_lp_token(lptoken_address).call()

    # 3: If the pool is not a Regular Pool or a V2 Pool then it's a Factory Pool. For Factory Pools, the pool_address = lptoken_address
    if pool_address == ZERO_ADDRESS:
        pool_address = lptoken_address
    
    return pool_address

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPTokenData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPTokenData(web3, lptoken_address, wallet, gauge_address, block, blockchain):

    lptoken_data = {}

    lptoken_data['contract'] = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)

    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()
    lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])

    lptoken_data['minter'] = getPoolAddress(web3, lptoken_address, block, blockchain)
    
    # # minter function retrieves the pool address
    # try:
    #     lptoken_data['minter'] = lptoken_data['contract'].functions.minter().call()
    # except:
    #     if lptoken_address == '0x4f3E8F405CF5aFC05D68142F3783bDfE13811522':#USDN/3CRV
    #         lptoken_data['minter'] = '0x0f9cb53Ebe405d49A0bbdBD291A65Ff571bC83e1'
    #     else:
    #         lptoken_data['minter'] = lptoken_address

    if gauge_address != None:
        lptoken_data['gauge'] = gauge_address
    else:
        lptoken_data['gauge'] = getPoolGaugeAddress(web3, lptoken_data['minter'], block, blockchain)

    if lptoken_data['gauge'] != None:
        lptoken_data['staked'] = balanceOf(wallet, lptoken_data['gauge'], block, blockchain, web3 = web3, decimals = lptoken_data['decimals'])
    else:
        lptoken_data['staked'] = 0
    
    lptoken_data['balanceOf'] = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    return lptoken_data

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
            # lptoken_contract = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)          
            
            # try:
            #     minter = lptoken_contract.functions.minter().call()
            # except:
            #     if lptoken_address == '0x4f3E8F405CF5aFC05D68142F3783bDfE13811522':  # USDN/3CRV
            #        minter = '0x0f9cb53Ebe405d49A0bbdBD291A65Ff571bC83e1'
            #     else:
            #         minter = lptoken_address

            minter = getPoolAddress(web3, lptoken_address, block, blockchain)

            gauge_address = getPoolGaugeAddress(web3, minter, block, blockchain)
        
        if gauge_address == None:
            return []

        # The ABI used to get the Gauge Contract is a general ABI for all types. This is because some gauges do not have 
        # their ABIs available in the explorers
        gauge_contract = getContract(gauge_address, blockchain, web3 = web3, abi = ABI_GAUGE, block = block)

        #-------------------
        # Liquidity Gauge V3
        #-------------------
        # This if is irrelevant right now becuase the ABI is hard-coded and has the methods of all the gauges versions
        # if 'claimable_reward_write' in str(gauge_contract.abi):
        # next_token = True
        # i = 0

        # try to avoid exceptions if the gauge is not Liquidity Gauge V3
        try:
            next_token = True
            i = 0

            while(next_token == True):
                token_address = gauge_contract.functions.reward_tokens(i).call()
                
                if token_address != ZERO_ADDRESS:
                    token_decimals = getDecimals(token_address, blockchain, web3 = web3)
                    token_reward = gauge_contract.functions.claimable_reward_write(wallet, token_address).call(block_identifier = block) / (10**token_decimals)

                    all_rewards.append([token_address, token_reward])

                    i += 1

                else:
                    next_token = False
                    break
        except:
                
            #-------------------
            # Liquidity Gauge V2
            #-------------------
            # This elif is irrelevant right now becuase the ABI is hard-coded and has the methods of all the gauges versions
            # elif 'reward_tokens' in str(gauge_contract.abi):
            next_token = True
            i = 0

            # try to avoid exceptions if gauge is not Liquidity Gauge V2
            try:
                while(next_token == True):
                
                    token_address = gauge_contract.functions.reward_tokens(i).call()
                    
                    if token_address != ZERO_ADDRESS:
                        token_decimals = getDecimals(token_address, blockchain, web3 = web3)
                        token_reward = gauge_contract.functions.claimable_reward(wallet, token_address).call(block_identifier = block) / (10**token_decimals)

                        all_rewards.append([token_address, token_reward])

                        i += 1

                    else:
                        next_token = False
                        break
            except:

                #-----------------------
                # Liquidity Gauge Reward
                #-----------------------
                # This elif is irrelevant right now becuase the ABI is hard-coded and has the methods of all the gauges versions
                # elif 'rewarded_token' in str(gauge_contract.abi):
                    
                # try to avoid exceptions if gauge is not Liquidity Gauge Reward
                try:
                    # CRV rewards
                    token_address = gauge_contract.functions.crv_token().call()
                    token_decimals = getDecimals(token_address, blockchain, web3 = web3)
                    token_reward = gauge_contract.functions.claimable_tokens(wallet).call(block_identifier = block) / (10**token_decimals)

                    all_rewards.append([token_address, token_reward])

                    # Additional rewards
                    token_address = gauge_contract.functions.rewarded_token().call()
                    token_decimals = getDecimals(token_address, blockchain, web3 = web3)
                    token_reward = (gauge_contract.function.claimable_reward(wallet).call(block_identifier = block) - gauge_contract.claimed_rewards_for(wallet).call(block_identifier = block)) / (10**token_decimals)

                    all_rewards.append([token_address, token_reward])
                
                except:

                    #----------------
                    # Liquidity Gauge
                    #----------------
                    # This else is irrelevant right now becuase the ABI is hard-coded and has the methods of all the gauges versions
                    # else:

                    # try to avoid exceptions if gauge is not Liquidity Gauge
                    try:
                        # CRV rewards
                        token_address = gauge_contract.functions.crv_token().call()
                        token_decimals = getDecimals(token_address, blockchain, web3 = web3)
                        token_reward = gauge_contract.functions.claimable_tokens(wallet).call(block_identifier = block) / (10**token_decimals)

                        all_rewards.append([token_address, token_reward])
                    
                    except:
                        pass
        
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
# CurveUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'convex_staked' = Staked LP Token Balance in Convex
# 'reward' = True -> retrieves the rewards / 'reward' = False or not passed onto the function -> no reward retrieval
# 'gauge_address' = gauge_address
# Output: a list with 2 elements:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance]
# 2 - List of Tuples: [reward_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CurveUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

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
        web3 = kwargs['web3']
    except:
        web3 = None
    
    try:
        index = kwargs['index']
    except:
        index = 0

    try:
        reward = kwargs['reward']
    except:
        reward = False
    
    try:
        convex_staked = kwargs['convex_staked']
    except:
        convex_staked = None
    
    try:
        gauge_address = kwargs['gauge_address']
    except:
        gauge_address = None
    
    try:
        if web3 == None: 
            web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)
        
        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)
        
        lptoken_data = getLPTokenData(web3, lptoken_address, wallet, gauge_address, block, blockchain)

        pool_contract = getContract(lptoken_data['minter'], blockchain, web3 = web3, abi = ABI_POOL, block = block)

        pool_balance_fraction = lptoken_data['balanceOf'] / lptoken_data['totalSupply']
        pool_staked_fraction =  lptoken_data['staked'] / lptoken_data['totalSupply']

        next_token = True
        i = 0

        while(next_token == True):
            
            try:
                token_address = pool_contract.functions.coins(i).call(block_identifier = block)
            except:
                next_token = False
                continue
            
            if token_address == E_ADDRESS:
                token_decimals = getDecimals(ZERO_ADDRESS, blockchain, web3 = web3)
            else:
                token_decimals = getDecimals(token_address, blockchain, web3 = web3) 

            balance = pool_contract.functions.balances(i).call(block_identifier = block)

            if convex_staked == None:
                token_balance = balance / (10**token_decimals) * (pool_balance_fraction)
                token_staked = balance / (10**token_decimals) * (pool_staked_fraction)

                balances.append([token_address, token_balance, token_staked])
            
            else:
                convex_pool_fraction = convex_staked / lptoken_data['totalSupply']
                token_staked = balance / (10**token_decimals) * convex_pool_fraction
                
                balances.append([token_address, token_staked])
            
            i += 1

        if reward == True:

            all_rewards = getAllRewards(wallet, lptoken_address, block, blockchain, web3 = web3, index = index, gauge_address = lptoken_data['gauge'])
            
            result.append(balances)
            result.append(all_rewards)
        
        else:
            result = balances

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return CurveUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return CurveUnderlying(wallet, lptoken_address, block, blockchain, index = index, reward = reward, execution = execution + 1)

    except Exception:
        return CurveUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, reward = reward, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CurveUnderlyingAmount
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# 'convex_staked' = Staked LP Token Balance in Convex
# 'gauge_address' = gauge_address
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance, staked_balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CurveUnderlyingAmount(lptoken_amount, lptoken_address, block, blockchain, **kwargs):

    balances = []

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
        gauge_address = kwargs['gauge_address']
    except:
        gauge_address = None

    try:
        if web3 == None:
            web3 = getNode(blockchain, block = block, index = index)

        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)

        lptoken_data = getLPTokenData(web3, lptoken_address, ZERO_ADDRESS, gauge_address, block, blockchain)

        pool_contract = getContract(lptoken_data['minter'], blockchain, web3 = web3, abi = ABI_POOL, block = block)

        pool_fraction = lptoken_amount / lptoken_data['totalSupply']

        next_token = True
        i = 0
        while (next_token == True):

            try:
                token_address = pool_contract.functions.coins(i).call(block_identifier = block)
            except:
                next_token = False
                continue

            if token_address == E_ADDRESS:
                token_decimals = getDecimals(ZERO_ADDRESS, blockchain, web3 = web3)
            else:
                token_decimals = getDecimals(token_address, blockchain, web3 = web3)

            balance = pool_contract.functions.balances(i).call(block_identifier = block)

            token_balance = balance / (10 ** token_decimals) * pool_fraction

            balances.append([token_address, token_balance, 0])

            i += 1

        return balances

    except GetNodeLatestIndexError:
        index = 0

        return CurveUnderlyingAmount(lptoken_amount, lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except GetNodeArchivalIndexError:
        index = 0

        return CurveUnderlyingAmount(lptoken_amount, lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return CurveUnderlyingAmount(lptoken_amount, lptoken_address, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CurvePoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 elements:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CurvePoolBalances(lptoken_address, block, blockchain, **kwargs):

    balances = []

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
        web3 = getNode(blockchain, block = block, index = index)
        
        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)
        
        # lptoken_contract = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)

        # try:
        #     minter = lptoken_contract.functions.minter().call()
        # except:
        #     if lptoken_address == '0x4f3E8F405CF5aFC05D68142F3783bDfE13811522':  # USDN/3CRV
        #         minter = '0x0f9cb53Ebe405d49A0bbdBD291A65Ff571bC83e1'
        #     else:
        #         minter = lptoken_address

        minter = getPoolAddress(web3, lptoken_address, block, blockchain)

        pool_contract = getContract(minter, blockchain, web3 = web3, abi = ABI_POOL, block = block)

        next_token = True
        i = 0
        while(next_token == True):
            
            try:
                token_address = pool_contract.functions.coins(i).call(block_identifier = block)
            except:
                next_token = False
                continue
            
            if token_address == E_ADDRESS:
                token_decimals = getDecimals(ZERO_ADDRESS, blockchain, web3 = web3)
            else:
                token_decimals = getDecimals(token_address, blockchain, web3 = web3) 

            balance = pool_contract.functions.balances(i).call(block_identifier = block)

            token_balance = balance / (10**token_decimals)

            balances.append([token_address, token_balance])
            
            i += 1

        return balances
    
    except GetNodeLatestIndexError:
        index = 0

        return CurvePoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return CurvePoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return CurvePoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)