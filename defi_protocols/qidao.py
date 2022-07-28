from defi_protocols._1inch import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# QIDAO_VAULTS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# QiDao Vaults List
QIDAO_VAULTS = [
    {
        'blockchain': XDAI,
        'vaults': [
            {
                'collateral': GNO_XDAI,
                'address': '0x014A177E9642d1b4E970418f894985dC1b85657f' # GNO Vault Address
            },
            {
                'collateral': WETH_XDAI,
                'address': '0x5c49b268c9841AFF1Cc3B0a418ff5c3442eE3F3b' # WETH Vault Address
            }
        ]
    },

    {
        'blockchain': POLYGON,
        'vaults': []
    }
]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GENERAL PARAMETERS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Coingecko cooldown time when request returns error 429
COINGECKO_COOLDOWN = 30

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Vault ABI - _minimumCollateralPercentage, checkCollateralPercentage, exists, getDebtCeiling, getEthPriceSource, getTokenPriceSource, mai, priceSourceDecimals, vaultCollateral, vaultDebt 
ABI_VAULT = '[{"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"_minimumCollateralPercentage","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"checkCollateralPercentage","inputs":[{"type":"uint256","name":"vaultID","internalType":"uint256"}],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"exists","inputs":[{"type":"uint256","name":"vaultID","internalType":"uint256"}],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"getDebtCeiling","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"getEthPriceSource","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"getTokenPriceSource","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"address","name":"","internalType":"contract ERC20Detailed"}],"name":"mai","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"priceSourceDecimals","inputs":[],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"vaultCollateral","inputs":[{"type":"uint256","name":"","internalType":"uint256"}],"constant":true}, {"type":"function","stateMutability":"view","payable":false,"outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"vaultDebt","inputs":[{"type":"uint256","name":"","internalType":"uint256"}],"constant":true}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getVaultAddress
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getVaultAddress(collateral_address, blockchain):

    vault_address = None

    for qidao_vault in QIDAO_VAULTS:

        if qidao_vault['blockchain'] == blockchain:

            for vault in qidao_vault['vaults']:

                if vault['collateral'] == collateral_address:

                    vault_address = vault['address']
                    break
            
            break
    
    return vault_address

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getQiDaoVaultData
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getQiDaoVaultData(vault_id, collateral_address, block, blockchain, **kwargs):

    vault_data = {}

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

        if not web3.isChecksumAddress(collateral_address):
            collateral_address = web3.toChecksumAddress(collateral_address)
        
        vault_address = getVaultAddress(collateral_address, blockchain)

        if vault_address != None:
            vault_contract = getContract(vault_address, blockchain, web3 = web3, block = block)

            if vault_contract.functions.exists(vault_id).call(block_identifier = block):

                debt_address = vault_contract.functions.mai().call()
                debt_decimals = getDecimals(debt_address, blockchain, web3 = web3)

                collateral_decimals = getDecimals(collateral_address, blockchain, web3 = web3)

                price_source_decimals = vault_contract.functions.priceSourceDecimals().call()

                # Collateral Address
                vault_data['collateral_address'] = collateral_address

                # Collateral Amount
                vault_data['collateral_amount'] = vault_contract.functions.vaultCollateral(vault_id).call(block_identifier = block) / (10**collateral_decimals)

                # Collateral Token USD Value
                vault_data['collateral_token_usd_value'] = vault_contract.functions.getEthPriceSource().call(block_identifier = block) / (10**price_source_decimals)

                # Debt Address
                vault_data['debt_address'] = debt_address
     
                # Debt Amount
                vault_data['debt_amount'] = vault_contract.functions.vaultDebt(vault_id).call(block_identifier = block) / (10**debt_decimals)
        
                # Debt Token USD Value
                # getTokenPriceSource() always returns MAI price = 1 USD. This is the price QiDao uses to calculate the Collateral Ratio.
                # MAI price might have depegged from USD so afterwards vault_data['debt_token_usd_value'] is overwritten with the price obtained from CoinGecko
                vault_data['debt_token_usd_value'] = vault_contract.functions.getTokenPriceSource().call(block_identifier = block) / (10**price_source_decimals)
        
                # Debt USD Value
                vault_data['debt_usd_value'] = vault_data['debt_amount'] * vault_data['debt_token_usd_value']

                 # Collateral Ratio
                vault_data['collateral_ratio'] = ((vault_data['collateral_amount'] * vault_data['collateral_token_usd_value']) / vault_data['debt_usd_value']) * 100

                # Available Debt Amount to Borrow
                vault_data['available_debt_amount'] = vault_contract.functions.getDebtCeiling().call(block_identifier = block) / (10**debt_decimals)

                # Liquidation Ratio
                vault_data['liquidation_ratio'] = vault_contract.functions._minimumCollateralPercentage().call(block_identifier = block)

                # Liquidation Price
                vault_data['liquidation_price'] = ((vault_data['liquidation_ratio'] / 100) * vault_data['debt_usd_value']) / vault_data['collateral_amount']

                # Debt Token USD Value OVERWRITTEN WITH COINGECKO'S PRICE
                vault_data['debt_token_usd_value'] = getPrice1inch(MAI_POL, 'latest', POLYGON)
                # price_data = getPriceCoinGecko(MAI_POL, math.floor(datetime.now().timestamp()), POLYGON)
                
                # while price_data[0] == 429:
                #     time.sleep(COINGECKO_COOLDOWN)
                #     price_data = getPriceCoinGecko(MAI_POL, math.floor(datetime.now().timestamp()), POLYGON)
                
                # vault_data['debt_token_usd_value'] = price_data[1][1]

        return vault_data

    except GetNodeLatestIndexError:
        index = 0

        return getQiDaoVaultData(vault_id, collateral_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0

        return getQiDaoVaultData(vault_id, collateral_address, block, blockchain, index = index, execution = execution + 1)
    
    except Exception:
        return getQiDaoVaultData(vault_id, collateral_address, block, blockchain, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# QiDaoUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output:
# 1 - Tuple: [[collateral_address, collateral_amount], [debt_address, -debt_amount]]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def QiDaoUnderlying(vault_id, collateral_address, block, blockchain, **kwargs):

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
        
        if not web3.isChecksumAddress(collateral_address):
            collateral_address = web3.toChecksumAddress(collateral_address)
        
        vault_address = getVaultAddress(collateral_address, blockchain)

        if vault_address != None:
            vault_contract = getContract(vault_address, blockchain, web3 = web3, block = block)

            if vault_contract.functions.exists(vault_id).call(block_identifier = block):
                
                collateral_decimals = getDecimals(collateral_address, blockchain, web3 = web3)
                collateral_amount = vault_contract.functions.vaultCollateral(vault_id).call(block_identifier = block) / (10**collateral_decimals)
                
                result.append([collateral_address, collateral_amount])

                debt_address = vault_contract.functions.mai().call()
                debt_decimals = getDecimals(debt_address, blockchain, web3 = web3)
                debt_amount = -1 * vault_contract.functions.vaultDebt(vault_id).call(block_identifier = block) / (10**debt_decimals)

                result.append([debt_address, debt_amount])

        return result

    except GetNodeLatestIndexError:
        index = 0

        return QiDaoUnderlying(vault_id, collateral_address, block, blockchain, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return QiDaoUnderlying(vault_id, collateral_address, block, blockchain, index = index, execution = execution + 1)

    except Exception:
        return QiDaoUnderlying(vault_id, collateral_address, block, blockchain, index = index + 1, execution = execution)