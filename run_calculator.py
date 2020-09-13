#!/usr/bin/python
# vim:ts=4:sts=4:sw=4:et:wrap:ai:fileencoding=utf-8:

import pdfplumber
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
        self.quantity = quantity if order_cat == 'C' else -quantity
        self.price = price
        self.total = price*self.quantity


def get_portfolio_based_on_orders(dict_orders):
    dict_portfolio = {}
    for stock_name, stock_orders in dict_orders.items():
        current_quantity = sum([stock_order.quantity for stock_order in stock_orders])
        total_cost = sum([stock_order.total for stock_order in stock_orders])
        average_cost = total_cost/current_quantity

        dict_portfolio[stock_name] = {'quantity': current_quantity,
                                      'total_cost': total_cost,
                                      'average_cost': average_cost
                                      }

    return dict_portfolio


dict_orders = {}

pdf = pdfplumber.open('nota_corretagem.pdf')
# pdf = pdfplumber.open('nota_bb.pdf')
# pdf = pdfplumber.open('nota_opcoes.pdf')

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
        if 'OPÇÃO' in market_cat: # TODO: check this
            deadline_idx = market_cat_idx+1
            stock_name_idx = market_cat_idx+2

        # stock name is separated in multiple columns. to join them, we need to find the next column (Quantity)
        # this assumes the Obs. column is empty (might mess things up)

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
        dict_orders.setdefault(stock_name, [])
        dict_orders[stock_name].append(current_order)

pdf.close()

dict_portfolio = get_portfolio_based_on_orders(dict_orders)
print (dict_portfolio)


