import asyncio

from bfxapi.rest.bfx_rest import BfxRest
from bfxapi import Order


class BfxClientWrapper:

    def __init__(self, API_KEY, API_SECRET):
        self.client = BfxRest(
            API_KEY=API_KEY,
            API_SECRET=API_SECRET,
            logLevel='DEBUG'
        )

    async def platform_status(self):
        response = await self.client.fetch("platform/status")
        return response

    def get_platform_status(self):
        t = asyncio.ensure_future(self.platform_status())
        status = asyncio.get_event_loop().run_until_complete(t)
        return status

    async def tickers(self, symbol):
        """ Get tickers for the given symbol. Tickers shows you the current best bid and ask,
        as well as the last trade price.

        symbol = format: t{}{} -> %First currency, %Second currency

        BfxRest.get_public_ticker(symbol)
        """
        ticker = await self.client.get_public_ticker(symbol)
        return Ticker(
            bid=ticker[0],
            ask=ticker[2],
            last_price=ticker[6],
            volume=ticker[7]
        )

    def get_ticker(self, symbol):
        try:
            t = asyncio.ensure_future(self.tickers(symbol))
            ticker = asyncio.get_event_loop().run_until_complete(t)
            return ticker
        except Exception as e:
            print(e)
            return None

    async def post_submit_order(self, symbol, amount, price):
        """ Submit Order

        amount = negative for sell, positive for buy

        BfxRest.submit_order(symbol,
                             price,
                             amount,
                             market_type='LIMIT',
                             hidden=False,
                             price_trailing=None,
                             price_aux_limit=None,
                             oco_stop_price=None,
                             close=False,
                             reduce_only=False,
                             post_only=False,
                             oco=False,
                             aff_code=None,
                             time_in_force=None,
                             leverage=None,
                             gid=None)
        """
        order = await self.client.submit_order(
            symbol=symbol,
            market_type=Order.Type.EXCHANGE_MARKET,
            amount=amount,
            price=price
        )
        return order

    def submit_order(self, symbol, amount, price):
        try:
            t = asyncio.ensure_future(self.post_submit_order(
                symbol=symbol,
                amount=amount,
                price=price
            ))
            order = asyncio.get_event_loop().run_until_complete(t)
            return order
        except Exception as e:
            print(e)
            return None

    def order_buy_market(self, symbol, amount):
        return self.submit_order(symbol, amount, 0)

    def order_sell_market(self, symbol, amount):
        return self.submit_order(symbol, -amount, 0)

    async def wallets(self):
        return await self.client.get_wallets()

    def get_wallets(self):
        try:
            t = asyncio.ensure_future(self.wallets())
            wallets = asyncio.get_event_loop().run_until_complete(t)
            return wallets
        except Exception as e:
            print(e)
            return None


class Ticker:
    def __init__(self, ask, bid, last_price, volume):
        self.ask = ask
        self.bid = bid
        self.last_price = last_price
        self.volume = volume
