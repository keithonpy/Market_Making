import datetime as dt
import time
import logging

from optibook.synchronous_client import Exchange

from math import floor, ceil
from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date

def trade_would_breach_position_limit(instrument_id, volume, side, position_limit):
    positions = exchange.get_positions()
    position_instrument = positions[instrument_id]

    if side == 'bid':
        return position_instrument + volume > position_limit
    elif side == 'ask':
        return position_instrument - volume < -position_limit
    else:
        raise Exception(f'''Invalid side provided: {side}, expecting 'bid' or 'ask'.''')




def insert_order(vol, stock_id, side, price):

    # Insert an IOC order to trade the opposing top-level, ensure to always keep instrument position below 5 so
    # aggregate position stays below 10.
    volume = vol
    if not trade_would_breach_position_limit(stock_id, volume, side, 1000):
        print(f'''Inserting {side} for {stock_id}: {volume:.0f} lot(s) at price {price:.2f}.''')
        exchange.insert_order(
            instrument_id=stock_id,
            price=price,
            volume=volume,
            side=side,
            order_type='limit')
        #return 0
    else:
        print(f'''Not inserting {volume:.0f} lot {side} for {stock_id} to avoid position-limit breach.''')
        #return 1






exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')


STOCK_ID = ['BAYER', 'SANTANDER', 'ING']
OPTIONS = [
    {'id': 'BAY-2022_03_18-050C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'call'},
    {'id': 'BAY-2022_03_18-050P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'put'},
    {'id': 'BAY-2022_03_18-075C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 75, 'callput': 'call'},
    {'id': 'BAY-2022_03_18-075P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 75, 'callput': 'put'},
    {'id': 'BAY-2022_03_18-100C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 100, 'callput': 'call'},
    {'id': 'BAY-2022_03_18-100P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 100, 'callput': 'put'},
    {'id': 'SAN-2022_03_18-040C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 40, 'callput': 'call'},
    {'id': 'SAN-2022_03_18-040P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 40, 'callput': 'put'},
    {'id': 'SAN-2022_03_18-050C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'call'},
    {'id': 'SAN-2022_03_18-050P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'put'},
    {'id': 'SAN-2022_03_18-060C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 60, 'callput': 'call'},
    {'id': 'SAN-2022_03_18-060P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 60, 'callput': 'put'},
    {'id': 'ING-2022_03_18-015C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 15, 'callput': 'call'},
    {'id': 'ING-2022_03_18-015P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 15, 'callput': 'put'},
    {'id': 'ING-2022_03_18-020C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 20, 'callput': 'call'},
    {'id': 'ING-2022_03_18-020P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 20, 'callput': 'put'},
    {'id': 'ING-2022_03_18-025C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 25, 'callput': 'call'},
    {'id': 'ING-2022_03_18-025P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 25, 'callput': 'put'},
   
]



    
positions = exchange.get_positions()
    
for p in positions:
    print(p, positions[p])
    print('clear all position')

time.sleep(1)    

# For each option
for option in OPTIONS:
    option_order_book = exchange.get_last_price_book(option['id'])
    bid_op = option_order_book.bids[0].price
    ask_op = option_order_book.asks[0].price
    
    pos = positions[option['id']]
    
    if  (pos > 0) :
        insert_order(pos, option['id'], 'ask', bid_op)
        
        
    elif (pos < 0) :
        insert_order(abs(pos), option['id'], 'bid', ask_op)

for stock in STOCK_ID:
    stock_order_book = exchange.get_last_price_book(stock)
    bid = stock_order_book.bids[0].price
    ask = stock_order_book.asks[0].price
    
    pos = positions[stock]
    
    if  pos > 0:
        insert_order(pos, stock, 'ask', bid)
            
    elif pos < 0:
        insert_order(abs(pos), stock, 'bid', ask)

# insert_order(700, STOCK_ID[0], 'ask', 70)


# Sleep until next iteration
print(f'\nSleeping for 4 seconds.')
time.sleep(4)
