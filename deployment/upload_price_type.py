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

    from backend.models.price import OrderPriceType
    from backend.libs.database import db

    file_path = cur_path + "/deployment/data/order_price_type.json"

    with codecs.open(file_path, 'r', 'utf-8') as f:
        types = json.load(f)

    for price_type in types:
        record = OrderPriceType(idx=price_type['idx'],
                                type_name=price_type['type_name'])
        db.session.add(record)
    db.session.commit()
