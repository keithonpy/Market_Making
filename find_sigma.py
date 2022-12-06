import datetime as dt
import time
import logging
import numpy as np


from optibook.synchronous_client import Exchange

from math import floor, ceil
from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date

exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')





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
    if not trade_would_breach_position_limit(stock_id, volume, side, 99):
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




STOCK_ID = ['BAYER', 'SANTANDER', 'ING']
OPTIONS = [
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-050C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-050P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'put', 'sigma': 4.0}, #
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-075C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 75, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-075P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 75, 'callput': 'put', 'sigma': 4.0}, #
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-100C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 100, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-100P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 100, 'callput': 'put', 'sigma': 4.0},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-040C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 40, 'callput': 'call', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-040P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 40, 'callput': 'put', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-050C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'call', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-050P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'put', 'sigma': 3.2}, #
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-060C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 60, 'callput': 'call', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-060P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 60, 'callput': 'put', 'sigma': 3.2}, #
    {'stock': 'ING', 'id': 'ING-2022_03_18-015C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 15, 'callput': 'call', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-015P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 15, 'callput': 'put', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-020C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 20, 'callput': 'call', 'sigma': 4.0}, #
    {'stock': 'ING', 'id': 'ING-2022_03_18-020P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 20, 'callput': 'put', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-025C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 25, 'callput': 'call', 'sigma':4.1},
    {'stock': 'ING', 'id': 'ING-2022_03_18-025P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 25, 'callput': 'put', 'sigma':4.0},
   
]


def find_sigma(OPTIONS, STOCK_ID):

    sigma_dict = {}
    
    
    for stock in STOCK_ID:
    
        stock_order_book = exchange.get_last_price_book(stock)
        
        bid = stock_order_book.bids[0].price
        ask = stock_order_book.asks[0].price
        bid_vol = stock_order_book.bids[0].volume
        ask_vol = stock_order_book.asks[0].volume
        
        
        S = (bid * bid_vol + ask * ask_vol) / (bid_vol + ask_vol)
        
        r = 0
        sigmas = np.arange(1, 9, 0.01)
            
        
        # For each option
        for option in OPTIONS:
            
            if option['stock'] == stock:
                T = calculate_current_time_to_date(option['expiry_date'])
                K = option['strike']
                
                for sigma in sigmas:
                
                    if option['callput'] == 'call':
                        val = call_value(S, K, T, r, sigma)
                    else:
                        val = put_value(S, K, T, r, sigma)
                    
                    
                    option_order_book = exchange.get_last_price_book(option['id'])
                    if (len(option_order_book.bids) == 0) | (len(option_order_book.asks) == 0):
                        continue
                    
                    bid_op = option_order_book.bids[0].price
                    ask_op = option_order_book.asks[0].price
                    bid_op_vol = option_order_book.bids[0].volume
                    ask_op_vol = option_order_book.asks[0].volume
                    
                    mid = (ask_op + bid_op) / 2
                    
                    if abs(mid - val) < 0.1:
                        sigma_dict[option['id']] = float(sigma)
                
                
            
            
    for key in sorted(sigma_dict):
        print(key, ':', sigma_dict[key])


def check_sigma(OPTIONS, STOCK_ID):
    for stock in STOCK_ID:
    
        stock_order_book = exchange.get_last_price_book(stock)
        
        bid = stock_order_book.bids[0].price
        ask = stock_order_book.asks[0].price
        bid_vol = stock_order_book.bids[0].volume
        ask_vol = stock_order_book.asks[0].volume
        
        
        S = (bid * bid_vol + ask * ask_vol) / (bid_vol + ask_vol)
        
        r = 0
        
            
        
        # For each option
        for option in OPTIONS:
            if option['stock'] == stock:
            
                sigma = option['sigma']
                T = calculate_current_time_to_date(option['expiry_date'])
                K = option['strike']
                
                
                
                if option['callput'] == 'call':
                    val = call_value(S, K, T, r, sigma)
                else:
                    val = put_value(S, K, T, r, sigma)
                
                
                option_order_book = exchange.get_last_price_book(option['id'])
                if (len(option_order_book.bids) == 0) | (len(option_order_book.asks) == 0):
                    continue
                
                bid_op = option_order_book.bids[0].price
                ask_op = option_order_book.asks[0].price
                bid_op_vol = option_order_book.bids[0].volume
                ask_op_vol = option_order_book.asks[0].volume
                
                mid = (ask_op + bid_op) / 2
                
                print(option['id'], ':' , mid, ',', val)
    



#check_sigma(OPTIONS, STOCK_ID)
find_sigma(OPTIONS, STOCK_ID)