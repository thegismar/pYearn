from web3 import Web3
import os
from datetime import datetime
import requests

infura = os.getenv('INFURA_WS')
etherscan_api = '7PFFRTS264XV42KD3GMP8Z7X9WA5QVHJBX'
ETHERSCAN_URL = 'https://api.etherscan.io/api?'


class ChainClient:

    def __init__(self):
        self.w3 = Web3(Web3.WebsocketProvider(infura))
        self.contract_address = {'yalink': '0x29e240cfd7946ba20895a7a02edb25c210f9f324',
                                 'ylink': '0x881b06da56BB5675c54E4Ed311c21E54C5025298',
                                 'usdc': '0xa2609B2b43AC0F5EbE27deB944d2a399C201E3dA',
                                 'crv': '0x5dbcf33d8c2e976c6b560249878e6f1491bca25c',
                                 'tusd': '0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a',
                                 'dai': '0xacd43e627e64355f1861cec6d3a6688b31a6f952',
                                 'usdt': '0x2f08119c6f07c006695e079aafc638b8789faf18'}
        self.initial_blocks = {'yalink': 10599617,
                               'ylink': 10604016,
                               'usdc': 10532708,
                               'crv': 10559448,
                               'tusd': 10603368,
                               'dai': 10650116,
                               'usdt': 10651402}
        self.blocks_in_year = 2425846
        self.blocks_in_week = 46523.073972606
        self.blocks_in_day = 6646.153424658
        self.blocks_in_hour = 276.923059361
        self.price_zero = 10 ** 18

    @staticmethod
    def get_address_checksum(address):
        return Web3.toChecksumAddress(address)

    def get_contract(self, address):
        return self.w3.eth.contract(address=address, abi=self.get_abi(address))

    def get_latest_block(self):
        return int(self.w3.eth.getBlock('latest')['number'])

    def get_block_at_time(self, seconds):
        delta_blocks = int(seconds / 15)
        return self.get_latest_block() - delta_blocks

    def get_block_time(self, block_number):
        block_time = self.w3.eth.getBlock(block_number)['timestamp']
        time_object = datetime.fromtimestamp(block_time)
        return time_object.strftime('%Y-%m-%d %H:%M')

    def get_share_price_at(self, vault):
        addy = self.contract_address[vault]
        addy_chsum = self.get_address_checksum(address=addy)
        return int(self.get_contract(address=addy_chsum).functions.getPricePerFullShare().call())

    @staticmethod
    def get_abi(contract_address):
        while True:
            resp = requests.get(
                f'{ETHERSCAN_URL}module=contract&action=getabi&address={contract_address}&apikey={etherscan_api}')

            if resp.status_code == 200:
                return resp.json()['result']

    def get_delta_block(self, vault):
        last_block = self.get_latest_block()
        first_block = self.initial_blocks[vault]

        last_price = self.get_share_price_at(vault)
        first_price = 10 ** 18

        return (last_price - first_price) / (last_block - first_block) / 10 ** 18

    def get_roi_hour(self, vault):
        return self.get_delta_block(vault) * self.blocks_in_hour

    def get_roi_day(self, vault):
        return self.get_delta_block(vault) * self.blocks_in_day

    def get_roi_week(self, vault):
        return self.get_delta_block(vault) * self.blocks_in_week

    def get_roi_year(self, vault):
        return self.get_delta_block(vault) * self.blocks_in_year
