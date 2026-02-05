import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc

# 1. Solidity Compiler setup
print("Solidity compiler version 0.8.0 install aagudhu...")
install_solc("0.8.0")

# 2. Updated Certificate.sol file-ah read panrom
# Ensure path: ./contract/Certificate.sol
# Old line: content = file.read()
# New line:
with open('contract/Certificate.sol', 'r', encoding='utf-8') as file:
    content = file.read()

# 3. Compile Logic
# Intha vatti compiled data-la 'Email, Dept, Year' fields-um sethu varum
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Certificate.sol": {"content": content}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.object"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

# 4. ABI and Bytecode extract panrom
# Contract name 'CertiChainMaster' nu irukatha confirm pannikonga
abi = compiled_sol["contracts"]["Certificate.sol"]["CertiChainMaster"]["abi"]
bytecode = compiled_sol["contracts"]["Certificate.sol"]["CertiChainMaster"]["evm"]["bytecode"]["object"]

# 5. Ganache Connection (Ganache open-la irukanum)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if not w3.is_connected():
    print("❌ Ganache connect aagala! Check if Ganache is running on 7545 port.")
    exit()

# Admin account (Ganache first address)
admin = w3.eth.accounts[0]

# 6. Contract Deployment
print("Pudhu features-oda contract deploy aagudhu...")
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Constructor empty-ah iruntha parameters thevai illai
tx_hash = Contract.constructor().transact({'from': admin})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

new_address = tx_receipt.contractAddress
print(f"✅ Success! Updated Contract Address: {new_address}")

# 7. IMPORTANT: Deployed Info save panrom
# Intha file-ah thaan main.py use pannum
data = {
    "address": new_address,
    "abi": abi
}
with open("deployed_info.json", "w") as f:
    json.dump(data, f)

print("Contract details 'deployed_info.json'-la save aayiduchu.")