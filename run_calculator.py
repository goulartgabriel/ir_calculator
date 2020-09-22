#!/usr/bin/python
# vim:ts=4:sts=4:sw=4:et:wrap:ai:fileencoding=utf-8:

import pdfplumber
import argparse

import pandas as pd

# USEFUL LINKS
# https://github.com/jsvine/pdfplumber#extracting-tables
# https://github.com/guilhermecgs/ir
# https://www.clubedopairico.com.br/temp/calculodeacoes.html


class orderInfo:
    def __init__(self, stock_name=None, date=None, order_cat=None, quantity=0, price=0):
        self.stock_name = stock_name
        self.date = date
        self.order_cat = order_cat
        self.quantity = quantity
        self.price = price
        self.total = price*self.quantity

def get_orders_dataframe(list_orders):
    df = pd.DataFrame({"date": [], "stock_name":[], "quantity":[], "price":[], "total_cost":[]},
        columns=["date","stock_name","order_cat","quantity","price","total_cost"])

    sorted_list_orders = sorted(list_orders, key=lambda x: x.date)
    for stock_order in sorted_list_orders:
        stock_df = pd.DataFrame({"date": [stock_order.date],
                                 "stock_name":[stock_order.stock_name],
                                 "order_cat": [stock_order.order_cat],
                                 "quantity":[stock_order.quantity],
                                 "price":[stock_order.price],
                                 "total_cost":[stock_order.total]},
                                 columns=["date","stock_name","order_cat","quantity","price","total_cost"])
        df = df.append(stock_df, ignore_index = True)

    return df

def get_portfolio_dict_based_on_orders(list_orders):
    dict_portfolio = {}
    stock_name_set = set([order.stock_name for order in list_orders])
    for stock_name in stock_name_set:

        stock_buy_quantity = sum([stock_order.quantity for stock_order in list_orders if stock_order.stock_name == stock_name and stock_order.order_cat == 'C'])
        stock_sell_quantity = sum([stock_order.quantity for stock_order in list_orders if stock_order.stock_name == stock_name and stock_order.order_cat == 'V'])
        total_buy_value = sum([stock_order.total for stock_order in list_orders if stock_order.stock_name == stock_name and stock_order.order_cat == 'C'])
        total_sell_value = sum([stock_order.total for stock_order in list_orders if stock_order.stock_name == stock_name and stock_order.order_cat == 'V'])

        net_quantity = stock_buy_quantity-stock_sell_quantity
        net_value = total_buy_value-total_sell_value
        average_cost = net_value/net_quantity

        dict_portfolio[stock_name] = {'quantity': net_quantity,
                                      'total_cost': net_value,
                                      'average_cost': average_cost
                                      }

    return dict_portfolio

def get_portfolio_dataframe(dict_portfolio):
    return pd.DataFrame.from_dict(dict_portfolio, orient='index')


def main(list_of_files):

    list_orders = []
    for filename in list_of_files:
        pdf = pdfplumber.open(filename)

        for page in pdf.pages:
            page = pdf.pages[0]

            ######### HEADER #########
            bounding_box = (page.width-80, 0, page.width, 70) # header (date, page)
            header = page.crop(bounding_box)
            header_text = header.extract_text()
            header_split_text = header_text.split("\n")
            date = header_split_text[1]    # might be overfitting

            ######### MAIN TABLE #########
            bounding_box = (0, 220, page.width, 460) # main table
            page = page.crop(bounding_box)
            text = page.extract_text()
            split_text = text.split("\n")

            for line in split_text:
                split_line = line.split(" ")
                unformatted_cleaned_line = [item for item in split_line if item != '']
                unformatted_cleaned_line = [item.replace('.','') for item in unformatted_cleaned_line]
                cleaned_line = [item.replace(',','.') for item in unformatted_cleaned_line]

                # columns
                # ['Q', 'Negociação', 'C/V', 'Tipo mercado', 'Prazo', 'Especificação do título', 'Obs.', 'Quantidade', 'Preço', 'Valor Operação', 'D/C']
                # assuming this as only category in "Negociacao" column
                if '1-BOVESPA' not in cleaned_line:
                    continue

                negotiation_idx = cleaned_line.index('1-BOVESPA')

                order_cat_idx = negotiation_idx+1
                order_cat = cleaned_line[order_cat_idx]
                market_cat_idx = order_cat_idx+1
                market_cat = cleaned_line[market_cat_idx]
                stock_name_idx = market_cat_idx+1
                if 'OPÇÃO' in market_cat:
                    # if order is related to options, column Prazo will be filled.
                    deadline_idx = market_cat_idx+1
                    stock_name_idx = market_cat_idx+2

                # stock name is separated in multiple columns. to join them, we need to find the next column (Quantity)
                # this assumes the Obs. column is empty (might mess things up for now - I've created an issue for this)

                stock_quantity_idx = None
                for i in range(stock_name_idx, len(cleaned_line)):
                    if cleaned_line[i].isdigit():
                        stock_quantity_idx = i
                        break

                stock_name = ' '.join(cleaned_line[stock_name_idx:stock_quantity_idx])
                stock_quantity = float(cleaned_line[stock_quantity_idx])
                stock_price_idx = stock_quantity_idx+1
                stock_price = float(cleaned_line[stock_price_idx])

                current_order = orderInfo(stock_name=stock_name, date=date, order_cat=order_cat, quantity=stock_quantity, price=stock_price)
                list_orders.append(current_order)

        pdf.close()

    dict_portfolio = get_portfolio_dict_based_on_orders(list_orders)
    df_orders = get_orders_dataframe(list_orders)
    df_portfolio =get_portfolio_dataframe(dict_portfolio)
    print (df_orders)
    print (df_portfolio)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--list_of_files", help="Input filenames in script path (e.g. -f nota_1.pdf,nota_2.pdf")

    args = parser.parse_args()

    list_of_files = args.list_of_files
    list_of_files = list_of_files.split(',')

    output = main(list_of_files)
    print (output)


