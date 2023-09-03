import codecs
import sys
import json

from os.path import dirname, abspath


def set_pythonpath():
    d = dirname(dirname(abspath(__file__)))
    sys.path.append(d)
    return d


def insert_to_database(address):
    from backend.models.order import OrderAddress
    from backend.libs.database import db

    key = list(address)[0]
    addr = address[key]
    top_addr = OrderAddress(region_name=key, full_region_name=key)
    db.session.add(top_addr)
    db.session.flush()

    for a in addr:
        full_region = '%s %s' % (key, a)
        first_addr = OrderAddress(region_name=a, full_region_name=full_region,
                                  parent_idx=top_addr.idx)
        db.session.add(first_addr)
        db.session.flush()
        for b in addr[a]:
            full_region = '%s %s %s' % (key, a, b)
            sec_addr = OrderAddress(region_name=b, parent_idx=first_addr.idx,
                                    full_region_name=full_region)
            if 'code' not in addr[a][b]:
                db.session.add(sec_addr)
                db.session.flush()
                for c, code in addr[a][b]['child'].items():
                    full_region = '%s %s %s %s' % (key, a, b, c)
                    third_addr = OrderAddress(region_name=c, price_code=code,
                                              full_region_name=full_region,
                                              parent_idx=sec_addr.idx)
                    db.session.add(third_addr)
            else:
                code = addr[a][b]['code']
                sec_addr.price_code = code
                db.session.add(sec_addr)

    db.session.commit()


def insert_sejong_to_database(address):
    from backend.models.order import OrderAddress
    from backend.libs.database import db

    key = list(address)[0]
    addr = address[key]
    top_addr = OrderAddress(region_name=key, full_region_name=key)
    db.session.add(top_addr)
    db.session.flush()

    for a in addr:
        full_region = '%s %s' % (key, a)
        first_addr = OrderAddress(region_name=a, full_region_name=full_region,
                                  parent_idx=top_addr.idx)

        if 'code' not in addr[a]:
            db.session.add(first_addr)
            db.session.flush()

            for c, code in addr[a]['child'].items():
                full_region = '%s %s %s' % (key, a, c)
                third_addr = OrderAddress(region_name=c, price_code=code,
                                          full_region_name=full_region,
                                          parent_idx=first_addr.idx)
                db.session.add(third_addr)
        else:
            first_addr.price_code = addr[a]['code']
            db.session.add(first_addr)
    db.session.commit()


if __name__ == '__main__':
    cur_path = set_pythonpath()

    file_path = cur_path + "/deployment/data/order_address.json"

    with codecs.open(file_path, 'r', 'utf-8') as f:
        addresses = json.load(f)

    for top_name in addresses.keys():
        if top_name == "세종특별자치시":
            insert_sejong_to_database({top_name: addresses[top_name]})
            continue

        insert_to_database({top_name: addresses[top_name]})

