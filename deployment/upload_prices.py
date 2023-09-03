import codecs
import sys
import json

from os.path import dirname, abspath


def set_pythonpath():
    d = dirname(dirname(abspath(__file__)))
    sys.path.append(d)
    return d


if __name__ == '__main__':
    cur_path = set_pythonpath()

    from backend.models.price import OrderPrice
    from backend.libs.database import db

    file_path = cur_path + "/deployment/data/prices.json"

    with codecs.open(file_path, 'r', 'utf-8') as f:
        prices = json.load(f)

    for price_entry in prices:
        code = price_entry['code']
        del price_entry['code']

        for floor, floor_price in price_entry.items():
            for price in floor_price:
                record = OrderPrice(code=code, floor=floor, type=price['type'],
                                    price=price['price'])

                db.session.add(record)
    db.session.commit()
