#!/usr/bin/python
# vim:ts=4:sts=4:sw=4:et:wrap:ai:fileencoding=utf-8:

import pdfplumber

pdf = pdfplumber.open('nota_corretagem.pdf')
page = pdf.pages[0]

# (x0, top, x1, bottom)
bounding_box = (0, 220, page.width, 450) # main table
bounding_box = (0, 0, page.width, 70) # header (date, page)
bounding_box = (0, 455, page.width, 700) # footnotes

print (page.width)

bounding_box = (0, 220, page.width, 460) # main table
page = page.crop(bounding_box)

text = page.extract_text()
print (text)


# 35-40, 40-90, 90-105, 105-160, 160-185, 185-305, 305-335, 335-390, 390-445, 445-540, 545-560


table_settings = {
    # "explicit_vertical_lines": [90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390],
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    # "intersection_x_tolerance": 10,
    # "text_x_tolerance": 150,
    }

table_settings = {
    "explicit_vertical_lines": [35, 40, 90, 105, 160, 185, 305, 335, 390, 445, 540, 560],
    "vertical_strategy": "explicit",
    # "horizontal_strategy": "text",
    # "intersection_x_tolerance": 10,
    # "text_x_tolerance": 150,
    }


tables = page.extract_table(table_settings=table_settings)
pdf.close()

for line in tables:
    print (line)
    print (len(line))

print ("==")
# # first item contains header and orders
# # second item contains summary and notes

# main_block = tables[0]
# for line in main_block:
#     print (line)
