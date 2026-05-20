import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from IPython.display import display, clear_output

def plotLimitOrderBook(book):
    # setup grid layout for displaying all 14 limit order books and a central limit order book consolidating data from all exchanges
    cols = 4
    rows = int(np.ceil(len(book.publisher_id_list) / cols))

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(24, 8 + 5 * rows))

    # increase white space so right-side labels don't overlap with the next column
    gs = gridspec.GridSpec(rows + 1, cols, figure=fig, height_ratios=[1.5] + [1]*rows, hspace=0.4, wspace=0.5)

    # create the massive central limit order book at the top
    ax_main = fig.add_subplot(gs[0, :])
    ax2_main = ax_main.twinx()

    # create the individual limit order books
    axes = []
    twin_axes = []
    for i in range(rows):
        for j in range(cols):
            ax = fig.add_subplot(gs[i+1, j])
            axes.append(ax)
            twin_axes.append(ax.twinx())

    national_bids = {}
    national_asks = {}

    for publisher_id in book.publisher_id_list:
        for p, order_dict in book.bids[publisher_id].items():
            if order_dict:
                national_bids[p] = national_bids.get(p, 0) + sum(order_dict.values())
                
        for p, order_dict in book.asks[publisher_id].items():
            if order_dict:
                national_asks[p] = national_asks.get(p, 0) + sum(order_dict.values())

    national_bid_prices = np.array(list(national_bids.keys()))
    national_bid_volumes = np.array(list(national_bids.values()))
    national_ask_prices = np.array(list(national_asks.keys()))
    national_ask_volumes = np.array(list(national_asks.values()))

    national_bid_sort_idx = np.argsort(national_bid_prices)[::-1]
    national_bid_prices = national_bid_prices[national_bid_sort_idx]
    national_bid_volumes = national_bid_volumes[national_bid_sort_idx]

    national_ask_sort_idx = np.argsort(national_ask_prices)
    national_ask_prices = national_ask_prices[national_ask_sort_idx]
    national_ask_volumes = national_ask_volumes[national_ask_sort_idx]

    # if there are no bids across all 14 equity exchanges then the highest price a stock can be sold for is 0 dollars
    national_best_bid_price = national_bid_prices[0] if len(national_bid_prices) > 0 else 0
    # if there are no asks across all 14 equity exchanges then the lowest price a stock can be bought for is infinite dollars
    national_best_ask_price = national_ask_prices[0] if len(national_ask_prices) > 0 else 1e9

    national_mid_price = (national_best_bid_price + national_best_ask_price) / 2
    national_spread = national_best_ask_price - national_best_bid_price 

    ####################### GRAPH THE CENTRAL LIMIT ORDER BOOK ############################
    #                                                                                     #
    #                                                                                     #
    #                                                                                     #
    ####################### GRAPH THE CENTRAL LIMIT ORDER BOOK ############################    
    ax_main.cla()
    ax2_main.cla()

    fixed_min_price = 650
    fixed_max_price = 750

    if len(national_bid_prices) > 0 and len(national_ask_prices) > 0:
        # set up a fixed range of prices for x-axis of limit order book histogram
        fixed_min_price = 650.00
        fixed_max_price = 750.00

        national_bid_mask = national_bid_prices >= fixed_min_price
        national_ask_mask = national_ask_prices <= fixed_max_price

        # frequency histogram of bids and asks at each price
        ax_main.bar(national_bid_prices[national_bid_mask], national_bid_volumes[national_bid_mask], color='#00FF00', label='Bids', alpha=0.5, width=0.01)
        ax_main.bar(national_ask_prices[national_ask_mask], national_ask_volumes[national_ask_mask], color='#FF0000', label='Asks', alpha=0.5, width=0.01)

        # cumulative frequency histogram of bids at each price
        ax2_main.step(national_bid_prices[national_bid_mask], np.cumsum(national_bid_volumes[national_bid_mask]), color='#00FF00', where='post')
        ax2_main.fill_between(national_bid_prices[national_bid_mask], np.cumsum(national_bid_volumes[national_bid_mask]), color='#00FF00', step='post', alpha=0.1)

        # cumulative frequency histogram of asks at each price
        ax2_main.step(national_ask_prices[national_ask_mask], np.cumsum(national_ask_volumes[national_ask_mask]), color='#FF0000', where='pre')
        ax2_main.fill_between(national_ask_prices[national_ask_mask], np.cumsum(national_ask_volumes[national_ask_mask]), color='#FF0000', step='pre', alpha=0.1)

        # national mid price
        ax_main.axvline(national_mid_price, color='white', linestyle=':')
    
    # only display values within the fixed range of prices [fixed_min_price, fixed_max_price]
    ax_main.set_xlim(fixed_min_price, fixed_max_price)
    ax_main.grid(color='gray', linestyle='--', alpha=0.3)
    ax_main.legend(loc='upper right')

    # the national volume for bids and asks
    ax_main.set_ylabel('Size')
    ax_main.yaxis.tick_left()
    ax_main.yaxis.set_label_position('left')

    # the cumulative volume for bids and asks
    ax2_main.set_ylabel('Cumulative Size')
    ax2_main.yaxis.tick_right()
    ax2_main.yaxis.set_label_position('right')

    # use cumulative maximum timestamp instead of ts_event for LOB reconstruction with jitter removed
    ax_main.set_title(
        f"CENTRAL LIMIT ORDER BOOK | TIMESTAMP: {book.last_update_time} | TOTAL ORDERS PROCESSSED: {book.total_orders_processed:,}\n"
        f"NATIONAL BEST BID: \${national_best_bid_price:.2f} | NATIONAL BEST ASK: \${national_best_ask_price:.2f} | SPREAD: \${national_spread:.2f} | MID: \${national_mid_price:.3f}",
        fontsize=20
    )

    ###################### GRAPH THE INDIVIDUAL LIMIT ORDER BOOKS #########################
    #                                                                                     #
    #                                                                                     #
    #                                                                                     #
    ###################### GRAPH THE INDIVIDUAL LIMIT ORDER BOOKS #########################   
    for idx, publisher_id in enumerate(book.publisher_id_list):
        ax = axes[idx]
        ax2 = twin_axes[idx]

        ax.cla()
        ax2.cla()

        # get the set of bids and asks for the individual exchange
        exchange_bids = book.bids[publisher_id]
        exchange_asks = book.asks[publisher_id]
        exchange_name = book.exchange_mapping[publisher_id]
        exchange_order_processed_total = book.order_processed_map[publisher_id]

        # if the limit order book of an individual exchange is empty, then state it is empty in the title and continue to the next limit order book without graphing anything
        if len(exchange_bids) == 0 or len(exchange_asks) == 0:
            ax.set_title(f"{exchange_name} | Orders: {exchange_order_processed_total:,} | LIMIT ORDER BOOK EMPTY", fontsize=10)
            ax.axis('off')
            ax2.axis('off')
            continue

        # the limit order book of an individual exchange contains a set of bids or a set of asks (it is nonempty)
        # run the same aggregation algorithm as the one for central limit order book, sorting bid and ask prices and extracting the best bid price, best bid size, best ask price, and best ask size
        
        exchange_bid_prices = np.array(list(exchange_bids.keys()))
        exchange_bid_volumes = np.array([sum(exchange_bids[p].values()) for p in exchange_bid_prices])

        exchange_ask_prices = np.array(list(exchange_asks.keys()))
        exchange_ask_volumes = np.array([sum(exchange_asks[p].values()) for p in exchange_ask_prices])

        exchange_bid_sort_idx = np.argsort(exchange_bid_prices)[::-1]
        exchange_bid_prices = exchange_bid_prices[exchange_bid_sort_idx]
        exchange_bid_volumes = exchange_bid_volumes[exchange_bid_sort_idx]

        exchange_ask_sort_idx = np.argsort(exchange_ask_prices)
        exchange_ask_prices = exchange_ask_prices[exchange_ask_sort_idx]
        exchange_ask_volumes = exchange_ask_volumes[exchange_ask_sort_idx]

        exchange_best_bid = exchange_bid_prices[0] if len(exchange_bid_prices) > 0 else 0
        exchange_best_ask = exchange_ask_prices[0] if len(exchange_ask_prices) > 0 else 1e9
        exchange_spread = exchange_best_ask - exchange_best_bid
        exchange_mid_price = (exchange_best_bid + exchange_best_ask) / 2

        exchange_bid_mask = exchange_bid_prices >= fixed_min_price
        exchange_ask_mask = exchange_ask_prices <= fixed_max_price

        ax.bar(exchange_bid_prices[exchange_bid_mask], exchange_bid_volumes[exchange_bid_mask], color='#00FF00', alpha=0.5, width=0.01)
        ax.bar(exchange_ask_prices[exchange_ask_mask], exchange_ask_volumes[exchange_ask_mask], color='#FF0000', alpha=0.5, width=0.01)

        ax2.step(exchange_bid_prices[exchange_bid_mask], np.cumsum(exchange_bid_volumes[exchange_bid_mask]), color='#00FF00', where='post')
        ax2.fill_between(exchange_bid_prices[exchange_bid_mask], np.cumsum(exchange_bid_volumes[exchange_bid_mask]), color='#00FF00', step='post', alpha=0.1)

        ax2.step(exchange_ask_prices[exchange_ask_mask], np.cumsum(exchange_ask_volumes[exchange_ask_mask]), color='#FF0000', where='pre')
        ax2.fill_between(exchange_ask_prices[exchange_ask_mask], np.cumsum(exchange_ask_volumes[exchange_ask_mask]), color='#FF0000', step='pre', alpha=0.1)

        ax.axvline(exchange_mid_price, color='white', linestyle=':')

        ax.set_title(
            f"{exchange_name} | Orders Processed: {exchange_order_processed_total:,}\n"
            f"Bid: \${exchange_best_bid:.2f} | Ask: \${exchange_best_ask:.2f} | Spread: \${exchange_spread:.2f} | Mid: \${exchange_mid_price:.3f}",
            fontsize=10
        )

        ax.grid(color='gray', linestyle='--', alpha=0.3)
        ax.set_xlim(fixed_min_price, fixed_max_price)

        ax.set_ylabel('Size')
        ax.yaxis.tick_left()
        ax.yaxis.set_label_position('left')

        ax2.set_ylabel('Cumulative Size')
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position('right')

    # hide any unused subplots
    for idx in range(len(book.publisher_id_list), len(axes)):
        axes[idx].cla()
        axes[idx].axis('off')
        twin_axes[idx].cla()
        twin_axes[idx].axis('off')
    
    plt.tight_layout()

    clear_output(wait=True)
    display(fig)

    plt.close()