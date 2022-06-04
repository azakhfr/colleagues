import argparse

from organisation.queries import (
    get_office_id_by_staff,
    get_staff_by_office_id,
    is_it_staff_id,
)
from prepare_data.work_with_file import recreate_data


parser = argparse.ArgumentParser(description="Search office colleagues")
parser.add_argument(
    "staff_id",
    type=int,
    metavar="company member id",
    help="uniq id company member, must by unsigned integer",
)
parser.add_argument(
    "--no-recreate",
    dest="no_recreate",
    help="if specified, the data will not be recreated",
    action="store_true",
)
args = parser.parse_args()

if args.no_recreate:
    recreate_data()


r = None
if is_it_staff_id(args.staff_id):
    office_id = get_office_id_by_staff(staff_id=args.staff_id)
    r = get_staff_by_office_id(office_id=office_id)
else:
    print(
        f"Company member with staff_id {args.staff_id} is not exist, please check your input."
    )

if r:
    print(" ".join(r))
