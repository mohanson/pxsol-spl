import argparse
import base64
import json
import pxsol
import random
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, default='11111111111111111111111111111112')
parser.add_argument('args', nargs='+')
args = parser.parse_args()

if args.net == 'develop':
    pxsol.config.current = pxsol.config.develop
if args.net == 'mainnet':
    pxsol.config.current = pxsol.config.mainnet
if args.net == 'testnet':
    pxsol.config.current = pxsol.config.testnet
pxsol.config.current.log = 1


def call(c: str):
    return subprocess.run(c, check=True, shell=True)


def info_save(k: str, v: str) -> None:
    with open('res/info.json', 'r') as f:
        info = json.load(f)
    info[k] = v
    with open('res/info.json', 'w') as f:
        json.dump(info, f, indent=4)


def info_load(k: str) -> str:
    with open('res/info.json', 'r') as f:
        info = json.load(f)
    return info[k]


def deploy():
    # Create spl mint
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(args.prikey))
    pxsol.log.debugln(f'main: create mint')
    pubkey_mint = user.spl_create(
        'Pxsol',
        'PXS',
        'https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json',
        9,
    )
    pxsol.log.debugln(f'main: create mint pubkey={pubkey_mint}')
    info_save('pubkey_mint', pubkey_mint.base58())

    # Mint spl tokens
    pxsol.log.debugln(f'main: mint 21000000 for {user.pubkey}')
    user.spl_mint(pubkey_mint, user.pubkey, 21000000 * 10**9)

    # Deploy spl mana
    call('cargo build-sbf -- -Znext-lockfile-bump')
    pxsol.log.debugln(f'main: deploy mana')
    with open('target/deploy/pxsol_spl.so', 'rb') as f:
        data = bytearray(f.read())
    pubkey_mana = user.program_deploy(data)
    pxsol.log.debugln(f'main: deploy mana pubkey={pubkey_mana}')
    info_save('pubkey_mana', pubkey_mana.base58())

    # Send spl tokens
    pubkey_mana_seed = bytearray([0x42])
    pubkey_mana_auth = pubkey_mana.derive_pda(pubkey_mana_seed)
    user.spl_transfer(pubkey_mint, pubkey_mana_auth, 20000000 * 10**9)


def update():
    # Update spl mana
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(args.prikey))
    pubkey_mana = pxsol.core.PubKey.base58_decode(info_load('pubkey_mana'))
    call('cargo build-sbf -- -Znext-lockfile-bump')
    pxsol.log.debugln(f'main: update mana')
    with open('target/deploy/pxsol_spl.so', 'rb') as f:
        user.program_update(pubkey_mana, bytearray(f.read()))


def genuser():
    pxsol.log.debugln(f'main: random user')
    user = pxsol.wallet.Wallet(pxsol.core.PriKey(bytearray(random.randbytes(32))))
    pxsol.log.debugln(f'main: random user prikey={user.prikey}')
    pxsol.log.debugln(f'main: random user pubkey={user.pubkey}')
    pxsol.log.debugln(f'main: request sol airdrop')
    txid = pxsol.rpc.request_airdrop(user.pubkey.base58(), 1 * pxsol.denomination.sol, {})
    pxsol.log.debugln(f'main: request sol airdrop txid={txid}')
    pxsol.rpc.wait([txid])
    pxsol.log.debugln(f'main: request sol airdrop done')


def airdrop():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(args.prikey))
    pubkey_mint = pxsol.core.PubKey.base58_decode(info_load('pubkey_mint'))
    pubkey_mana = pxsol.core.PubKey.base58_decode(info_load('pubkey_mana'))
    pubkey_mana_seed = bytearray([0x42])
    pubkey_mana_auth = pubkey_mana.derive_pda(pubkey_mana_seed)
    void = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    void.pubkey = pubkey_mana_auth
    pubkey_mana_spla = void.spl_account(pubkey_mint)
    rq = pxsol.core.Requisition(pubkey_mana, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(user.spl_account(pubkey_mint), 1))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mana, 0))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mana_auth, 0))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mana_spla, 1))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mint, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.AssociatedTokenAccount.pubkey, 0))
    rq.data = bytearray()
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    pxsol.log.debugln(f'main: request spl airdrop')
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    tlog = pxsol.rpc.get_transaction(txid, {})
    for e in tlog['meta']['logMessages']:
        pxsol.log.debugln(e)
    splcnt = user.spl_balance(pubkey_mint)
    pxsol.log.debugln(f'main: request spl airdrop done recv={splcnt[0] / 10**splcnt[1]}')


if __name__ == '__main__':
    eval(f'{args.args[0]}()')
