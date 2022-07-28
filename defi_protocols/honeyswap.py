from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LP Token ABI - decimals, totalSupply, getReserves, balanceOf, token0, token1
ABI_LPTOKEN = '[{"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint8","name":"","internalType":"uint8"}],"name":"decimals","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"totalSupply","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint112","name":"_reserve0","internalType":"uint112"},{"type":"uint112","name":"_reserve1","internalType":"uint112"},{"type":"uint32","name":"_blockTimestampLast","internalType":"uint32"}],"name":"getReserves","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"balanceOf","inputs":[{"type":"address","name":"","internalType":"address"}],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"address"}],"name":"token0","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"address"}],"name":"token1","inputs":[],"constant":true}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getLPTokenData
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getLPTokenData(web3, lptoken_address, wallet, block, blockchain):

    lptoken_data = {}
     
    lptoken_data['contract'] = getContract(lptoken_address, blockchain, web3 = web3, abi = ABI_LPTOKEN, block = block)
    
    lptoken_data['decimals'] = lptoken_data['contract'].functions.decimals().call()
    lptoken_data['totalSupply'] = lptoken_data['contract'].functions.totalSupply().call(block_identifier = block) / (10**lptoken_data['decimals'])
    lptoken_data['reserves'] = lptoken_data['contract'].functions.getReserves().call(block_identifier = block)

    lptoken_data['balanceOf'] = lptoken_data['contract'].functions.balanceOf(wallet).call(block_identifier = block) / (10**lptoken_data['decimals'])

    return lptoken_data

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# HoneyswapUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def HoneyswapUnderlying(wallet, lptoken_address, block, blockchain, **kwargs):

    result = []

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

        if not web3.isChecksumAddress(wallet):
            wallet = web3.toChecksumAddress(wallet)
        
        if not web3.isChecksumAddress(lptoken_address):
            lptoken_address = web3.toChecksumAddress(lptoken_address)
        
        lptoken_data = getLPTokenData(web3, lptoken_address, wallet, block, blockchain)

        pool_balance_fraction = lptoken_data['balanceOf'] / lptoken_data['totalSupply']

        for i in range(len(lptoken_data['reserves'])):
            try:
                func = getattr(lptoken_data['contract'].functions, 'token' + str(i))
            except:
                continue
            
            token_address = func().call()
            token_decimals = getDecimals(token_address, blockchain, web3 = web3)

            token_balance = lptoken_data['reserves'][i] / (10**token_decimals) * (pool_balance_fraction)

            result.append([token_address, token_balance])

        return result

    except GetNodeLatestIndexError:
        index = 0

        return HoneyswapUnderlying(wallet, lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return HoneyswapUnderlying(wallet, lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return HoneyswapUnderlying(wallet, lptoken_address, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# HoneyswapPoolBalances
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output: a list with 1 element:
# 1 - List of Tuples: [liquidity_token_address, balance]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def HoneyswapPoolBalances(lptoken_address, block, blockchain, **kwargs):

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

        return HoneyswapPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return HoneyswapPoolBalances(lptoken_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return HoneyswapPoolBalances(lptoken_address, block, blockchain, index = index + 1, execution = execution)