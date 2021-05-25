import json

import asyncio

from src.whitebit.rest import WhiteBitClient
from src.bitfinex.rest import BfxClientWrapper, Ticker
import schedule
from src.celery.celery import app


BITFINEX_API_KEY = "L3tAktqOf7YxQ1zVoxlqjUk0PztTREj5tfiqdzoIMoR"
BITFINEX_API_SECRET = "hyp4Txyt3IVsaGx5zGqegoeL1pZV6Uh65VCEMvOe1Lk"

WHITEBIT_API_KEY = "a6b88c85d2e229b6bd80b089e8f57245"
WHITEBOIT_API_SECRET = "0ae248a4132d384f0c379d2ef503cc09"

EXCHANGE_PAIR1 = "tNEOUSD"
EXCHANGE_PAIR2 = "NEO_USDT"
DIFF = 0.1
TIME_DURATION = 5  # in seconds
AMOUNT = 5

bfxClient = BfxClientWrapper(
    API_KEY=BITFINEX_API_KEY,
    API_SECRET=BITFINEX_API_SECRET
)

whiteBitClient = WhiteBitClient(
    API_KEY=WHITEBIT_API_KEY,
    API_SECRET=WHITEBOIT_API_SECRET
)


class ArbitrageBot:

    def __init__(
        self,
        wb_client: WhiteBitClient,
        bfx_client: BfxClientWrapper,
        diff: int,
        bfx_paritet: str,
        wb_paritet: str,
        amount: float
    ):
        self.diff = diff/100
        self.wb_client = wb_client
        self.bfx_client = bfx_client
        self.bfx_paritet = bfx_paritet
        self.wb_paritet = wb_paritet
        self.amount = amount

    @staticmethod
    def get_mid_price(bid, ask):
        return (bid + ask) / 2

    def function1(self, b1_bid, b2_ask, b1_mid, b2_mid):
        """
        If B1 %X greater than A2
        bitfinex => sell
        whitebit => buy
        """
        difference = (b1_bid - b2_ask) / b1_bid
        if difference < self.diff:
            return

        print("B1_BID " + str(b1_bid) + " GREATER THAN B2_ASK " + str(b2_ask) + " FOR " + str(self.diff))

        bitfinex_amount = self.amount / b1_mid
        whitebit_amount = self.amount

        bitfinex_order = self.bfx_client.order_sell_market(self.bfx_paritet, bitfinex_amount)
        whitebit_order = self.wb_client.buy_order_market(self.wb_paritet, whitebit_amount)

        try:
            if whitebit_order is not None:
                print("====== Whitebit Order ======")
                print(json.dumps(whitebit_order.json(), sort_keys=True, indent=4))

            if bitfinex_order is not None:
                print("====== Bitfinex Order ======")
                print("symbol: ", bitfinex_order.notify_info.symbol)
                print("amount: ", bitfinex_order.notify_info.amount)
                print("type: ", bitfinex_order.notify_info.type)
                print("price: ", bitfinex_order.notify_info.price)
                print("status: ", bitfinex_order.notify_info.status)

        except Exception as e:
            print(e)

    def function2(self, b1_ask, b2_bid, b1_mid, b2_mid):
        """
        If B2 %X greater than A1
        bitfinex => buy
        whitebit => sell
        """
        difference = (b2_bid - b1_ask) / b2_bid
        if difference < self.diff:
            return

        print("B2_BID " + str(b2_bid) + " GREATER THAN B1_ASK " + str(b1_ask) + " FOR " + str(self.diff))

        bitfinex_amount = self.amount / b1_mid
        whitebit_amount = self.amount / b2_mid
        print("wb: ", whitebit_amount)
        print("bfx: ", bitfinex_amount)

        whitebit_order = self.wb_client.sell_order_market(self.wb_paritet, whitebit_amount)
        bitfinex_order = self.bfx_client.order_buy_market(self.bfx_paritet, bitfinex_amount)

        try:
            if whitebit_order is not None:
                print("====== Whitebit Order ======")
                print(json.dumps(whitebit_order.json(), sort_keys=True, indent=4))

            if bitfinex_order is not None:
                print("====== Bitfinex Order ======")
                print("symbol: ", bitfinex_order.notify_info.symbol)
                print("amount: ", bitfinex_order.notify_info.amount)
                print("type: ", bitfinex_order.notify_info.type)
                print("price: ", bitfinex_order.notify_info.price)
                print("status: ", bitfinex_order.notify_info.status)

        except Exception as e:
            print(e)

    def execute(self):
        """
        GET current tickers from whitebit and bitfinex
        """
        ticker1: Ticker = self.bfx_client.get_ticker(self.bfx_paritet)
        ticker2: dict = self.wb_client.ticker(self.wb_paritet)

        bitfinex_wallet = self.bfx_client.get_wallets()
        whitebit_wallet = self.wb_client.get_wallets()

        if bitfinex_wallet is None:
            return

        print("====== Bitfinex ======")
        for wallet in bitfinex_wallet:
            print(wallet.balance, wallet.currency)

        print("====== Whitebit ======")
        currency_first = self.wb_paritet.split("_")[0]
        currency_second = self.wb_paritet.split("_")[1]
        print(currency_first, whitebit_wallet["result"][currency_first])
        print(currency_second, whitebit_wallet["result"][currency_second])

        if ticker1 is None or ticker2 is None:
            return

        b1_bid = float(ticker1.bid)
        b1_ask = float(ticker1.ask)
        b2_ask = float(ticker2["result"]["ask"])
        b2_bid = float(ticker2["result"]["bid"])
        b1_mid = self.get_mid_price(b1_bid, b1_ask)
        b2_mid = self.get_mid_price(b2_bid, b2_ask)

        print("B1: bid price: " + str(ticker1.bid))
        print("B1: ask price: " + str(ticker1.ask))
        print("B2: bid price: " + str(ticker2["result"]["bid"]))
        print("B2: ask price: " + str(ticker2["result"]["ask"]))
        print()

        """
        Function 1 and Function 2
        """
        self.function1(b1_bid, b2_ask, b1_mid, b2_mid)
        self.function2(b1_ask, b2_bid, b1_mid, b2_mid)


arbitrage_bot = ArbitrageBot(whiteBitClient, bfxClient, DIFF, EXCHANGE_PAIR1, EXCHANGE_PAIR2, AMOUNT)


"""
First and BETTER FASTER VERSION FOR PERIODIC TASK
    To run:
    1 - command:
        start redis server
    2 - command:
        celery -A src beat -l info
    3 - command to another terminal
        celery -A src worker -l info --pool=solo

"""


@app.task
def periodic():
    arbitrage_bot.execute()

"""
Second and NORM not fast VERSION FOR PERIODIC TASK only 1 sec max
"""


def test_schedule():
    arbitrage_bot.execute()


schedule.every(TIME_DURATION).seconds.do(test_schedule)

while True:
    schedule.run_pending()
