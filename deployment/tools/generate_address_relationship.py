import sys

from os.path import dirname, abspath


def set_pythonpath():
    d = dirname(dirname(abspath(__file__)))
    sys.path.append(d)
    return d


def get_interest_address(full_region_name):
    from backend.models.interest_address import InterestAddress
    sections = full_region_name.split(' ')
    int_addr = InterestAddress.query.filter_by(region_name=sections[0]) \
        .first()
    if int_addr is not None:
        name = '%s %s' % (sections[0], sections[1])
        int_addr2 = InterestAddress.query.filter_by(full_region_name=name) \
            .first()
        if int_addr2 is None:
            return int_addr
        else:
            return int_addr2
    return int_addr


def process_matching_address():
    from backend.models.address_relation import AddressRelation
    from backend.models.order import OrderAddress
    from backend.libs.database import db

    order_addrs = OrderAddress.query.filter(OrderAddress.price_code.isnot(None)
                                            ).all()
    for order_addr in order_addrs:
        int_addr = get_interest_address(order_addr.full_region_name)
        addr = AddressRelation(interest_idx=int_addr.idx,
                               order_addr_idx=order_addr.idx)
        db.session.add(addr)
    db.session.commit()

if __name__ == '__main__':
    set_pythonpath()

    process_matching_address()
