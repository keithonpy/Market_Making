import datetime as dt
import time
import logging
import numpy as np
import csv
import time
from optibook.synchronous_client import Exchange

from math import floor, ceil
from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date


#check position limit
def trade_would_breach_position_limit(instrument_id, volume, side, position_limit=300):
    positions = exchange.get_positions()
    position_instrument = positions[instrument_id]

    if side == 'bid':
        return position_instrument + volume > position_limit
    elif side == 'ask':
        return position_instrument - volume < -position_limit
    else:
        raise Exception(f'''Invalid side provided: {side}, expecting 'bid' or 'ask'.''')



# insert order function
def insert_order(volume, stock_id, side, price, order_type):
    if not trade_would_breach_position_limit(stock_id, volume, side, 300):
        print(f'''Inserting {side} for {stock_id}: {volume:.0f} lot(s) at price {price:.2f}.''')
        exchange.insert_order(
            instrument_id=stock_id,
            price=price,
            volume=volume,
            side=side,
            order_type=order_type)
        return 0
    else:
        print(f'''Not inserting {volume:.0f} lot {side} for {stock_id} to avoid position-limit breach.''')


        return 1

########################################################################################################################
#Cointegration function

def cointegration(exchange, STOCK_IDS, gamma, c, vol):
    check_lim = 0
    stock_id_y = STOCK_IDS[0]
    stock_id_x = STOCK_IDS[1]
    print(f'Cointegration stock {STOCK_IDS} to trade.')

    # Obtain order book and only trade if there are both bids and offers available on that stock
    stock_order_book_x = exchange.get_last_price_book(stock_id_x)

    stock_order_book_y = exchange.get_last_price_book(stock_id_y)

    if not (stock_order_book_x and stock_order_book_x.bids and stock_order_book_x.asks):
        return print(f'Order book for {stock_id_x} does not have bids or offers. Skipping iteration.')


    if not (stock_order_book_y and stock_order_book_y.bids and stock_order_book_y.asks):
        return print(f'Order book for {stock_id_y} does not have bids or offers. Skipping iteration.')

    # Obtain best bid and ask prices from order book
    best_bid_price_x = stock_order_book_x.bids[0].price
    best_ask_price_x = stock_order_book_x.asks[0].price
    best_bid_price_y = stock_order_book_y.bids[0].price
    best_ask_price_y = stock_order_book_y.asks[0].price


    # gamma = 1.25

    # c = -0.573
    # vol = 1
    mid_price_x = (best_bid_price_x + best_ask_price_x) / 2
    mid_price_y = (best_bid_price_y + best_ask_price_y) / 2


    z = np.log(best_bid_price_y) - (c + gamma * np.log(best_ask_price_x))
    # z = np.log(mid_price_y) - (c + gamma * np.log(mid_price_x))
    print(f'value of z (action when z > 0): {z}')

    if z > 0:
        side_y = 'ask'
        price_y = best_bid_price_y

        #positions = exchange.get_positions()

        volume_y = vol

        side_x = 'bid'
        price_x = best_ask_price_x

        volume_x = round( vol * gamma * price_y / price_x, 0)
        # insert ioc order for pair trading
        check = insert_order(volume_y, stock_id_y, side_y, price_y, 'ioc')
        check_lim += check
        check = insert_order(volume_x, stock_id_x, side_x, price_x, 'ioc')
        check_lim += check



    # z = np.log(best_ask_price_y) - (c + gamma * np.log(best_ask_price_x))
    z = np.log(best_ask_price_y) - (c + gamma * np.log(best_bid_price_x))
    print(f'value of z (action when z < 0): {z}')
    if z < 0:
        side_y = 'bid'
        price_y = best_ask_price_y

        volume_y = vol

        # Insert an IOC order to trade the opposing top-level


        side_x = 'bid'
        price_x = best_ask_price_x


        volume_x = round(vol * gamma * price_y / price_x, 0)
        check = insert_order(volume_y, stock_id_y, side_y, price_y, 'ioc')
        
        check = insert_order(volume_x, stock_id_x, side_x, price_x, 'ioc')
    
    
    # # # do ioc again    
    # positions = exchange.get_positions()
    # pos_y = positions[stock_id_y]
    # pos_x = positions[stock_id_x]
    # stock_order_book_x = exchange.get_last_price_book(stock_id_x)
    # stock_order_book_y = exchange.get_last_price_book(stock_id_y)
    
    
    
    # if pos_y > 0:
    #     if pos_y > abs(int(gamma * mid_price_y / mid_price_x) * pos_x):
            
    #         volume_x = abs(pos_y) -  abs(int(gamma * mid_price_y / mid_price_x) * pos_x)
    #         side_x = 'ask'
    #         price_x = stock_order_book_x.bids[0].price
    #         check = insert_order(volume_x, stock_id_x, side_x, price_x, 'ioc')
    #     elif abs(pos_y) < abs(int(gamma * mid_price_y / mid_price_x) * pos_x):
    #         volume_x = abs(int(gamma * mid_price_y / mid_price_x) * pos_x) - pos_y
    #         side_x = 'bid'
    #         price_x = stock_order_book_x.asks[0].price
    #         check = insert_order(volume_x, stock_id_x, side_x, price_x, 'ioc')
            
    # if pos_y < 0:
    #     if abs(pos_y) > int(gamma * mid_price_y / mid_price_x) * pos_x:
            
    #         volume_x = abs(pos_y) -  abs(int(gamma * mid_price_y / mid_price_x) * pos_x)
    #         side_x = 'bid'
    #         price_x = stock_order_book_x.asks[0].price
    #         check = insert_order(volume_x, stock_id_x, side_x, price_x, 'ioc')
    #     elif abs(pos_y) < abs(int(gamma * mid_price_y / mid_price_x) * pos_x):
    #         volume_x = abs(int(gamma * mid_price_y / mid_price_x) * pos_x) - abs(pos_y)
    #         side_x = 'ask'
    #         price_x = stock_order_book_x.bids[0].price
    #         check = insert_order(volume_x, stock_id_x, side_x, price_x, 'ioc')
            
    # print(f'\nSleeping for 2 seconds.')
    # time.sleep(2)

######################################################################################################################################
#Option Market Maker
def optionmm(exchange, STOCK_ID, OPTIONS):
    check_lim = 0
    delta = {'BAYER': 0, 'SANTANDER' : 0, 'ING': 0}
    for stock in STOCK_ID:
        stock_order_book = exchange.get_last_price_book(stock)
        if (len(stock_order_book.bids) == 0) | (len(stock_order_book.asks) == 0):
                continue
        bid = stock_order_book.bids[0].price
        ask = stock_order_book.asks[0].price
        bid_vol = stock_order_book.bids[0].volume
        ask_vol = stock_order_book.asks[0].volume


        S = (bid * bid_vol + ask * ask_vol) / (bid_vol + ask_vol)

        r = 0



        # For each option
        for option in OPTIONS:
            if option['stock'] != stock:
                continue
            # Print which option we are updating
            print(f'''Updating option {option['id']} with expiry date {option['expiry_date']}, strike {option['strike']} '''
                  f'''and type {option['callput']}.''')

            # TODO: Delete existing orders
            outstanding = exchange.get_outstanding_orders(option['id'])
            for o in outstanding.values():
                result = exchange.delete_order(option['id'], order_id=o.order_id)
                print(f"Deleted order id {o.order_id}: {result}")
            # TODO: Calculate option value
            # Spot is average of current bid and current ask

            T = calculate_current_time_to_date(option['expiry_date'])
            K = option['strike']
            sigma = option['sigma']


            if option['callput'] == 'call':
                fair_val = call_value(S, K, T, r, sigma)
            else:
                fair_val = put_value(S, K, T, r, sigma)


            option_order_book = exchange.get_last_price_book(option['id'])
            if (len(option_order_book.bids) == 0) | (len(option_order_book.asks) == 0):
                continue

            bid_op = option_order_book.bids[0].price
            ask_op = option_order_book.asks[0].price
            bid_op_vol = option_order_book.bids[0].volume
            ask_op_vol = option_order_book.asks[0].volume


            offset = 0.1
            # offset = (ask_op - bid_op) / 2
            # offset_ask = (ask_op - bid_op) *bid_op_vol / (bid_op_vol +  ask_op_vol)
            # offset_bid = (ask_op - bid_op) *ask_op_vol / (bid_op_vol +  ask_op_vol)
            vol = 30
            # TODO: Calculate desired bid and ask prices
            desired_bid = float(round((fair_val - offset), 1))
            desired_ask = float(round((fair_val + offset), 1))
            # desired_bid = float(round((fair_val - offset_bid), 1))
            # desired_ask = float(round((fair_val + offset_ask), 1))
            # TODO: Insert limit orders on those prices for a desired volume
            check = insert_order(vol, option['id'], 'ask', desired_ask, 'limit')
            # check_lim +=check
            check = insert_order(vol, option['id'], 'bid', desired_bid, 'limit')
            # check_lim += check
            # Wait 1/10th of a second to avoid breaching the exchange frequency limit
            time.sleep(0.10)

        # TODO: Calculate current delta position across all instruments

        for option in OPTIONS:
            if option['stock'] != stock:
                continue

            T = calculate_current_time_to_date(option['expiry_date'])
            K = option['strike']
            sigma = option['sigma']
            positions = exchange.get_positions()



            lots = positions[option['id']]

            if option['callput'] == 'call':
                d = call_delta(S, K, T, r, sigma)
            else:
                d = put_delta(S, K, T, r, sigma)

            delta[stock] += d * lots

        # TODO: Calculate stocks to buy/sell to become close to delta-neutral
        delta[stock] += positions[stock]


        # TODO: Perform the hedging stock trade by inserting an IOC order on the stock against the current top-of-book
        if int(delta[stock]) > 0:
            check = insert_order(int(delta[stock]), stock, 'ask', bid, 'ioc')
            check_lim += check

        elif int(delta[stock]) < 0:
            check = insert_order(abs(int(delta[stock])), stock, 'bid', ask, 'ioc')
            check_lim += check

    return check_lim

###################################################################################################################################
def createcsv(filename, STOCK_ID, OPTIONS):
    fieldnames = ['time', 'pnl']
    for s in STOCK_ID:
        fieldnames.append(s)
    for o in OPTIONS:
        fieldnames.append(o['id'])
    with open(filename, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    return fieldnames


###################################################################################################################################
# clear half the position of all financial instuments only execute when the stock reaches position limit
def clear_half_position(exchange, STOCK_ID, OPTIONS):

    positions = exchange.get_positions()
    for stock in STOCK_ID:
        for option in OPTIONS:
            if option['stock'] != stock:
                continue
            outstanding = exchange.get_outstanding_orders(option['id'])
            for o in outstanding.values():
                result = exchange.delete_order(option['id'], order_id=o.order_id)
                print(f"Deleted order id {o.order_id}: {result}")
        
        
        
        for option in OPTIONS:
            if option['stock'] != stock:
                continue
            option_order_book = exchange.get_last_price_book(option['id'])
            bid_op = option_order_book.bids[0].price
            ask_op = option_order_book.asks[0].price
    
            pos = positions[option['id']]
    
            if  (pos > 0) & (int(pos/2) != 0) :
                insert_order(int(pos/2), option['id'], 'ask', bid_op, 'ioc')
    
    
            elif (pos < 0) & (abs(int(pos/2)) != 0):
                insert_order(abs(int(pos/2)), option['id'], 'bid', ask_op, 'ioc')
    
        
        stock_order_book = exchange.get_last_price_book(stock)
        bid = stock_order_book.bids[0].price
        ask = stock_order_book.asks[0].price

        pos = positions[stock]

        if  pos > 0 & (int(pos/2) != 0):
            insert_order(int(pos/2), stock, 'ask', bid, 'ioc')

        elif pos < 0 & (abs(int(pos/2)) != 0):
            insert_order(abs(int(pos/2)), stock, 'bid', ask, 'ioc')
            
        print('Sleep for 1 seconds')
        time.sleep(1)
    return 0
    

##################################################################################################################################################
def decide_delta():
    pass



exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')


STOCK_ID = ['BAYER', 'SANTANDER', 'ING']
OPTIONS = [
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-050C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-050P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'put', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-075C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 75, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-075P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 75, 'callput': 'put', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-100C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 100, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'BAYER', 'id': 'BAY-2022_03_18-100P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 100, 'callput': 'put', 'sigma': 4.0},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-040C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 40, 'callput': 'call', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-040P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 40, 'callput': 'put', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-050C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'call', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-050P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 50, 'callput': 'put', 'sigma': 3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-060C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 60, 'callput': 'call', 'sigma':3.2},
    {'stock': 'SANTANDER', 'id': 'SAN-2022_03_18-060P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 60, 'callput': 'put', 'sigma': 3.2},
    {'stock': 'ING', 'id': 'ING-2022_03_18-015C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 15, 'callput': 'call', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-015P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 15, 'callput': 'put', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-020C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 20, 'callput': 'call', 'sigma': 4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-020P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 20, 'callput': 'put', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-025C', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 25, 'callput': 'call', 'sigma':4.0},
    {'stock': 'ING', 'id': 'ING-2022_03_18-025P', 'expiry_date': dt.datetime(2022, 3, 18, 12, 0, 0), 'strike': 25, 'callput': 'put', 'sigma':4.0},

]

# filename = 'coint.csv'
# fieldnames = createcsv(filename, STOCK_ID, OPTIONS)

check_lim = 0
update = 0

while True:
    print(f'')
    print(f'-----------------------------------------------------------------')
    print(f'TRADE LOOP ITERATION ENTERED AT {str(dt.datetime.now()):18s} UTC.')
    print(f'-----------------------------------------------------------------')

    #########################################
    #  Implement your main trade loop here  #
    #########################################

     

    initialpnl = exchange.get_pnl()
    start = time.time()
    
    
    if check_lim >= 1:
        check_lim = clear_half_position(exchange, STOCK_ID, OPTIONS)
        update = 0
    else:
        check_lim = optionmm(exchange, STOCK_ID, OPTIONS)
        if (check_lim >= 1) & (update == 0):
            cointegration(exchange, ['BAYER', 'SANTANDER'], 1.25, -0.573, 30)
            update = 1
        


    # Sleep until next iteration
    print(f'\nSleeping for 5 seconds.')
    time.sleep(5)
    # pnl = exchange.get_pnl() - initialpnl
    # data = {}
    # data['time'] = time.time() - start
    # data['pnl'] = pnl
    # positions = exchange.get_positions()
    # for key, value in positions.items():
    #     data[key] = value
    # with open(filename, mode='a') as csv_file:
    #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    #     writer.writerow(data)



