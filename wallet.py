import subprocess
import json
from web3 import Web3
from bit import Key

from constants import *

def derive_wallets(mnemonic_phrase, coin_list):
    coin_dict={}
    for coin in coin_list:
        command = f"php ./hd-wallet-derive/hd-wallet-derive.php -g --format=json --coin={coin} --numderive=3 --mnemonic={mnemonic}"
        addresses = json.loads(subprocess.check_output(command, shell=True))
        coin_dict.update({coin:addresses})
    return coin_dict

def priv_key_to_acct(coin, index):
    wallets = derive_wallets(mnemonic, coins)
    priv_key = wallets[coin][index]["privkey"]
    if coin == "btc-test":
        return PrivateKeyTestnet(priv_key)
    else:
        return Account.privateKeyToAccount(priv_key)
        
def create_tx(account, coin, to, amount):
    if coin == "btc-test":
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    else:
        gas_est = w3.eth.estimateGas(
        {
            'from':account.address,
            'to':to,
            'value':amount,
        }
        )
        return {
        'from':account.address,
        'to':to,
        'value':amount,
        'gasPrice':w3.eth.gasPrice,
        'gas':gas_est,
        'nonce': w3.eth.getTransactionCount(account.address)
        }

def send_tx(coin, to, amount):
    account = priv_key_to_acct(coin, 0)
    tx = create_tx(account, coin, to, amount)
    if coin == "eth":
        signed_tx = account.sign_transaction(tx)
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    else:
        signed_tx = account.sign_transaction(tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)