import argparse
import base64
import json
import pxsol
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
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


def step_create_mint():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(info_load('prikey')))
    pxsol.log.debugln(f'main: create mint')
    pubkey_mint = user.spl_create(
        'Pxsol',
        'PXS',
        'https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json',
        9,
    )
    pxsol.log.debugln(f'main: create mint pubkey={pubkey_mint}')
    info_save('pubkey_mint', pubkey_mint.base58())


def step_create_info_rs():
    pubkey_mint = pxsol.core.PubKey.base58_decode(info_load('pubkey_mint'))
    pxsol.log.debugln(f'main: create info.rs')
    with open('src/info.rs', 'w') as f:
        f.write('pub const PUBKEY_MINT: [u8; 32] = [')
        f.write('\n')
        f.write('    ')
        for i in range(0x00, 0x10):
            f.write(f'0x{pubkey_mint.p[i]:02x},')
            if i != 0x0f:
                f.write(' ')
        f.write('\n')
        f.write('    ')
        for i in range(0x10, 0x20):
            f.write(f'0x{pubkey_mint.p[i]:02x},')
            if i != 0x1f:
                f.write(' ')
        f.write('\n')
        f.write('];')
        f.write('\n')


def step_mint():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(info_load('prikey')))
    pubkey_mint = pxsol.core.PubKey.base58_decode(info_load('pubkey_mint'))
    pxsol.log.debugln(f'main: mint 21000000 for {user.pubkey}')
    user.spl_mint(pubkey_mint, user.pubkey, 21000000 * 10**9)


def step_deploy_mana():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(info_load('prikey')))
    call('cargo build-sbf -- -Znext-lockfile-bump')
    pxsol.log.debugln(f'main: deploy mana')
    with open('target/deploy/pxsol_spl.so', 'rb') as f:
        pubkey_mana = user.program_deploy(f.read())
    pxsol.log.debugln(f'main: deploy mana pubkey={pubkey_mana}')
    info_save('pubkey_mana', pubkey_mana.base58())


def step_update_mana():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(info_load('prikey')))
    pubkey_mana = pxsol.core.PubKey.base58_decode(info_load('pubkey_mana'))
    call('cargo build-sbf -- -Znext-lockfile-bump')
    pxsol.log.debugln(f'main: update mana')
    with open('target/deploy/pxsol_spl.so', 'rb') as f:
        user.program_update(pubkey_mana, f.read())


def step_create_pool():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(info_load('prikey')))
    pubkey_mint = pxsol.core.PubKey.base58_decode(info_load('pubkey_mint'))
    pubkey_mana = pxsol.core.PubKey.base58_decode(info_load('pubkey_mana'))
    pubkey_mana_auth = pubkey_mana.derive_pda(bytearray([0x00]))
    user.spl_transfer(pubkey_mint, pubkey_mana_auth, 10500000 * 10**9)


def step_call():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(info_load('prikey')))
    pubkey_mint = pxsol.core.PubKey.base58_decode(info_load('pubkey_mint'))
    pubkey_mana = pxsol.core.PubKey.base58_decode(info_load('pubkey_mana'))
    pubkey_mana_auth = pubkey_mana.derive_pda(bytearray([0x00]))
    void = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    void.pubkey = pubkey_mana_auth
    pubkey_mana_spla = void.spl_account(pubkey_mint)
    rq = pxsol.core.Requisition(pubkey_mana, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(user.spl_account(pubkey_mint), 1))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mana, 0))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mana_spla, 1))
    rq.account.append(pxsol.core.AccountMeta(pubkey_mint, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.AssociatedTokenAccount.pubkey, 0))
    rq.data = bytearray()
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    tlog = pxsol.rpc.get_transaction(txid, {})
    for e in tlog['meta']['logMessages']:
        pxsol.log.debugln(e)


def step_main():
    step_create_mint()
    step_mint()
    step_deploy_mana()
    step_create_pool()
    step_call()


step_update_mana()
step_call()
