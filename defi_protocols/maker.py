from general.blockchain_functions import *

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CDP MANAGER
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CDP Manager Contract Address
CDP_MANAGER_ADDRESS = '0x5ef30b9986345249bc32d8928B7ee64DE9435E39'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ILK REGISTRY
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ilk Registry Contract Address
ILK_REGISTRY_ADDRESS = '0x5a464C28D19848f44199D003BeF5ecc87d090F87'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# VAT
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Vat Contract Address
VAT_ADDRESS = '0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SPOT
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Spot Contract Address
SPOT_ADDRESS = '0x65C79fcB50Ca1594B025960e539eD7A9a6D434A3'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ABIs
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CDP Manager ABI - ilks, urns
ABI_CDP_MANAGER = '[{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"ilks","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"urns","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'

# Ilk Registry ABI - info
ABI_ILK_REGISTRY = '[{"inputs":[{"internalType":"bytes32","name":"ilk","type":"bytes32"}],"name":"info","outputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint256","name":"class","type":"uint256"},{"internalType":"uint256","name":"dec","type":"uint256"},{"internalType":"address","name":"gem","type":"address"},{"internalType":"address","name":"pip","type":"address"},{"internalType":"address","name":"join","type":"address"},{"internalType":"address","name":"xlip","type":"address"}],"stateMutability":"view","type":"function"}]'

# Vat ABI - urns, ilks
ABI_VAT = '[{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"},{"internalType":"address","name":"","type":"address"}],"name":"urns","outputs":[{"internalType":"uint256","name":"ink","type":"uint256"},{"internalType":"uint256","name":"art","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}, {"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"ilks","outputs":[{"internalType":"uint256","name":"Art","type":"uint256"},{"internalType":"uint256","name":"rate","type":"uint256"},{"internalType":"uint256","name":"spot","type":"uint256"},{"internalType":"uint256","name":"line","type":"uint256"},{"internalType":"uint256","name":"dust","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'

# Spot ABI - ilks
ABI_SPOT = '[{"constant":true,"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"ilks","outputs":[{"internalType":"contract PipLike","name":"pip","type":"address"},{"internalType":"uint256","name":"mat","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# getMakerVaultData
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'web3' = web3 (Node) -> Improves performance
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getMakerVaultData(vault_id, block, **kwargs):

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
            web3 = getNode(ETHEREUM, block = block, index = index)

        cpd_manager_contract = getContract(CDP_MANAGER_ADDRESS, ETHEREUM, web3 = web3, abi = ABI_CDP_MANAGER, block = block)
        ilk_registry_contract = getContract(ILK_REGISTRY_ADDRESS, ETHEREUM, web3 = web3, abi = ABI_ILK_REGISTRY, block = block)
        vat_contract = getContract(VAT_ADDRESS, ETHEREUM, web3 = web3, abi = ABI_VAT, block = block)
        spot_contract = getContract(SPOT_ADDRESS, ETHEREUM, web3 = web3, abi = ABI_SPOT, block = block)
    
        ilk = cpd_manager_contract.functions.ilks(vault_id).call(block_identifier = block)

        ilk_info = ilk_registry_contract.functions.info(ilk).call()

        urn_handler_address = cpd_manager_contract.functions.urns(vault_id).call(block_identifier = block)

        urn_data = vat_contract.functions.urns(ilk, urn_handler_address).call(block_identifier = block)
        
        vault_data['mat'] = spot_contract.functions.ilks(ilk).call(block_identifier = block)[1] / 10**27
        vault_data['gem'] = ilk_info[4]
        vault_data['dai'] = DAI_ETH
        vault_data['ink'] = urn_data[0] / 10**18
        vault_data['art'] = urn_data[1] / 10**18
        
        ilk_data = vat_contract.functions.ilks(ilk).call(block_identifier = block)
        
        vault_data['Art'] = ilk_data[0] / 10**18
        vault_data['rate'] = ilk_data[1] / 10**27
        vault_data['spot'] = ilk_data[2] / 10**27
        vault_data['line'] = ilk_data[3] / 10**45
        vault_data['dust'] = ilk_data[4] / 10**45

        return vault_data
    
    except GetNodeLatestIndexError:
        index = 0

        return getMakerVaultData(vault_id, block, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0

        return getMakerVaultData(vault_id, block, index = index, execution = execution + 1)
    
    except Exception:
        return getMakerVaultData(vault_id, block, index = index + 1, execution = execution)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MakerUnderlying
# **kwargs:
# 'execution' = the current iteration, as the function goes through the different Full/Archival nodes of the blockchain attempting a successfull execution
# 'index' = specifies the index of the Archival or Full Node that will be retrieved by the getNode() function
# Output:
# 1 - Tuple: [[collateral_address, collateral_amount], [debt_address, -debt_amount]]
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def MakerUnderlying(vault_id, block, **kwargs):

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
        web3 = getNode(ETHEREUM, block = block, index = index)

        vault_data = getMakerVaultData(vault_id, block, web3 = web3, index = index)

        # Append the Collateral Address and Balance to result[]
        result.append([vault_data['gem'], vault_data['ink']])

        # Append the Debt Address (DAI Address) and Balance to result[]
        total_debt = (vault_data['art'] * vault_data['rate']) * -1
        result.append([vault_data['dai'], total_debt])

        return result
    
    except GetNodeLatestIndexError:
        index = 0

        return MakerUnderlying(vault_id, block, index = index, execution = execution + 1)
    
    except GetNodeArchivalIndexError:
        index = 0
        
        return MakerUnderlying(vault_id, block, index = index, execution = execution + 1)

    except Exception:
        return MakerUnderlying(vault_id, block, index = index + 1, execution = execution)