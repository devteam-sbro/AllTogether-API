import codecs
import json
import os

from xlrd import open_workbook

base_dir = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..', 'address'))


def parse_address_list(addresses):
    zz = dict()
    for a in addresses:
        al = a.split(' ')
        a1 = al[0]
        a2 = al[1]
        a3 = al[2]

        if a1 not in zz:
            zz[a1] = dict()

        if a2 not in zz[a1]:
            zz[a1][a2] = dict()

        if a3 not in zz[a1][a2]:
            zz[a1][a2][a3] = dict()

        if len(al) == 4:
            zz[a1][a2][a3]['code'] = al[3]
            zz[a1][a2][a3]['child'] = ''
        elif len(al) == 5:
            if 'child' not in zz[a1][a2][a3]:
                zz[a1][a2][a3]['child'] = dict()
            zz[a1][a2][a3]['child'][al[3]] = al[4]
    return zz


def build_address_list(sheet):
    addresses = []
    for nrow in range(1, sheet.nrows):
        row = sheet.row(nrow)
        addresses.append(
            ' '.join(x.value for x in row[:7] if x.value is not ''))
    return addresses


def get_interest_idx(name):
    return 1


def insert_to_database(address):
    key = list(address)[0]
    addr = address[key]
    for a in addr:
        for b in addr[a]:
            if 'code' not in addr[a][b]:
                for c, code in addr[a][b]['child'].items():
                    fullname = '%s %s %s %s - %s' % (key, a, b, c, code)
                    print(fullname)
            else:
                fullname = '%s %s %s - code : %s' % (key, a, b,
                                                     addr[a][b]['code'])
                print(fullname)


def parse_sejong_address_list(address):
    zz = dict()
    for a in address:
        al = a.split(' ')
        a1 = al[0]
        a2 = al[1]

        if a1 not in zz:
            zz[a1] = dict()

        if a2 not in zz[a1]:
            zz[a1][a2] = dict()

        if len(al) == 3:
            zz[a1][a2]['code'] = al[2]
            zz[a1][a2]['child'] = ''
        elif len(al) == 4:
            if 'child' not in zz[a1][a2]:
                zz[a1][a2]['child'] = dict()
            zz[a1][a2]['child'][al[2]] = al[3]
    return zz


def insert_sejong_to_database(address):
    key = list(address)[0]
    addr = address[key]
    for a in addr:
        if 'code' not in addr[a]:
            for c, code in addr[a]['child'].items():
                fullname = '%s %s %s - %s' % (key, a, c, code)
                print(fullname)
        else:
            fullname = '%s %s - code : %s' % (key, a, addr[a]['code'])
            print(fullname)


if __name__ == '__main__':
    result = dict()
    for xls_file in os.listdir(base_dir):
        file_path = '%s/%s' % (base_dir, xls_file)

        workbook = open_workbook(file_path)

        sheet = workbook.sheet_by_index(0)
        addresses = build_address_list(sheet)
        if 'sejong' in file_path:
            parsed_addr = parse_sejong_address_list(addresses)
            # insert_sejong_to_database(parsed_addr)
        else:
            parsed_addr = parse_address_list(addresses)
            # insert_to_database(parsed_addr)

        key = list(parsed_addr)[0]
        result[key] = parsed_addr[key]

    with codecs.open('order_address.json', 'w', 'utf-8') as c:
        c.write((json.dumps(result, indent=2).encode('utf-8')).
                decode('unicode-escape'))
