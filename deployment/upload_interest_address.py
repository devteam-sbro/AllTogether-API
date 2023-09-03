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

    from backend.models.interest_address import InterestAddress
    from backend.libs.database import db

    address_file = cur_path+"/deployment/data/interest_address.json"
    with codecs.open(address_file, 'r', 'utf-8') as f:
        address = json.load(f)

    for region in address:
        region_name = next(iter(region.keys()))
        sub_regions = region[region_name]

        region = InterestAddress(region_name=region_name,
                                 full_region_name=region_name)
        db.session.add(region)
        db.session.commit()

        print(region_name)
        parent_idx = region.idx
        for subregion in sub_regions:
            full_region_name = '%s %s' % (region_name, subregion)
            sub = InterestAddress(region_name=subregion, parent_idx=parent_idx,
                                  full_region_name=full_region_name)
            db.session.add(sub)
            print("-- " + subregion)

        db.session.commit()




