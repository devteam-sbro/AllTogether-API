import codecs
import json
import os

from xlrd import open_workbook

file_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '..',
                                        'price.xlsx'))

if __name__ == '__main__':
    workbook = open_workbook(file_dir)

    prices = []
    for nsheet in range(0, 27):
        sheet = workbook.sheets()[nsheet]
        price_code = sheet.name
        code_entry = {'code': price_code}
        for nrow in range(1, sheet.nrows):
            row = sheet.row(nrow)
            floor = int(row[0].value)
            code_entry[floor] = []
            for i in range(1, len(row) - 1):
                code_entry[floor].append(
                    {'type': i, 'price': int(row[i].value)})

        prices.append(code_entry)

    with codecs.open('prices.json', 'w', 'utf-8') as c:
        c.write((json.dumps(prices, indent=2).encode('utf-8')).
                decode('unicode-escape'))
