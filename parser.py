import collections
import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path

HEADER_FIELD = '.m.Pay Date'

FIELDS_ORDER = [
    HEADER_FIELD, '.m.Pay', '.m.',
    '.d.p',
    '.d.d',
    '.d.t',
    '.d.et',
    '.d.ytd',
]

UNWANTED_FIELDS = [
    '.m.Company Name', '.m.Account', '.m.Sort Code', '.m.NI Number', '.m.NI Category', '.m.Pay Method',
]


def parse_amount(amount: str):
    amount = amount.replace(',', '')
    if amount.endswith('-'):
        return -float(amount[:-1])
    else:
        return float(amount)


def parse_metadata(metadata_text: str):
    metadata = {}
    for row in metadata_text.splitlines():
        if not row:
            continue
        _, cell1, cell2, cell3, _ = row.split('|')
        for cell in [cell1, cell2, cell3]:
            cell = cell.strip()
            if cell:
                separator_regex = r':\s+' if ':' in cell else r'\s\s+'
                item, value = re.compile(separator_regex).split(cell, maxsplit=1)
                metadata[item.strip()] = value.strip()

    return metadata


def parse_payments_table(payments_table: str):
    payments = {}
    deductions = {}
    ytd_balances = {}
    for row in payments_table.splitlines():
        row = row.strip()
        if not row:
            continue
        _, payment, deduction, ytd_balance, _ = row.split('|')

        payment = payment.strip()
        if payment:
            payment_item, amount = re.compile(r'\s\s+').split(payment)
            payments[payment_item] = parse_amount(amount)

        deduction = deduction.strip()
        if deduction:
            deduction_item, amount = re.compile(r'\s\s+').split(deduction)
            deductions[deduction_item] = parse_amount(amount)

        ytd_balance = ytd_balance.strip()
        if ytd_balance:
            ytd_balance_item, amount = re.compile(r'\s\s+').split(ytd_balance)
            ytd_balances[ytd_balance_item] = parse_amount(amount)

    return payments, deductions, ytd_balances


def parse_totals(totals_row: str):
    totals = {}
    _, payment_total, deduction_total, net_pay, _ = totals_row.split('|')
    for total_value in [payment_total, deduction_total, net_pay]:
        item, amount = re.compile(r':\s+').split(total_value.strip())
        totals[item] = parse_amount(amount)
    return totals


def parse_employer_totals(employer_total_footer):
    totals = {}
    for row in employer_total_footer.strip().splitlines()[1:]:
        row = row.strip()
        if not row or row.count('|') != 4:
            continue

        _, this_employer_cell, _ = row.split('|', maxsplit=2)
        item, amount = re.compile(r'\s\s+').split(this_employer_cell.strip())
        totals[item] = parse_amount(amount)
    return totals


def parse_payslip(payslip_text: str):
    address, metadata, payment_data = re.compile(r"^\s+?-+$", re.MULTILINE).split(payslip_text)

    _, payment_headers, payments_table, totals_row, _, employer_total_footer = \
        re.compile(r"^\s+?-+\|$", re.MULTILINE).split(payment_data)

    metadata = parse_metadata(metadata)
    payments, deductions, ytd_balances = parse_payments_table(payments_table)
    totals = parse_totals(totals_row)
    employer_totals = parse_employer_totals(employer_total_footer)

    data = {
        'p': payments,
        'd': deductions,
        'ytd': ytd_balances,
        't': totals,
        'et': employer_totals
    }
    return {
        # 'address': address,
        'm': metadata,
        'd': data
    }


def print_payslip(dd, indent=""):
    for k, v in dd.items():
        if not hasattr(v, 'items'):
            print(f"{k}:\n{v}")
            # print(['*'] * 30)
        else:
            print(f"{k}:\n")
            print_payslip(v, indent=indent + "    ")


def count_fields(counts, nested_dict, prefix=''):
    if hasattr(nested_dict, 'items'):
        for k, v in nested_dict.items():
            count_fields(counts, v, prefix=prefix + '.' + k)
    else:
        counts[prefix] += 1


def flatten(nested_dict, flat_dict, prefix=''):
    if hasattr(nested_dict, 'items'):
        for k, v in nested_dict.items():
            flatten(v, flat_dict, prefix=prefix + '.' + k)
    else:
        flat_dict[prefix] = nested_dict


def write_payslip_csv_month_rows(categories, csv_table):
    with open('payslips-month-rows.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=categories)
        writer.writeheader()
        for row in csv_table:
            writer.writerow(row)


def write_payslip_csv_month_columns(columns, csv_table):
    with open('payslips-month-columns.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        # writer.writeheader()
        for row in csv_table:
            writer.writerow(row)


def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    from itertools import tee
    from itertools import filterfalse
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)


def enforce_order(iterable, prefixes: list):
    remainder = iterable
    result = []
    for prefix in prefixes:
        remainder, matching = partition(lambda x: x.startswith(prefix), remainder)
        remainder = list(remainder)
        result += sorted(matching)
    result += sorted(remainder)
    return result


if __name__ == '__main__':
    payslips_dir = Path(sys.argv[1])
    counts = collections.Counter()
    csv_rows_table = []
    for payslip_file in sorted(payslips_dir.glob('*.txt')):
        # if payslip_file.name < '2018-04-' or payslip_file.name > '2019-04-':
        #     continue
        payslip_text = payslip_file.read_text(encoding='utf-8')
        if 'Employee Number' not in payslip_text:
            print(f"Skipping {payslip_file} ...")
            continue
        print(f"Parsing {payslip_file} ...")
        payslip = parse_payslip(payslip_text)

        count_fields(counts, payslip)
        flat_payslip = {}
        flatten(payslip, flat_payslip)
        csv_rows_table.append(flat_payslip)

    categories = counts.keys()
    categories = enforce_order(categories, FIELDS_ORDER)

    # pprint('\n'.join(categories))
    # print(len(categories))
    write_payslip_csv_month_rows(categories, csv_rows_table)

    for unwanted_field in UNWANTED_FIELDS:
        categories.remove(unwanted_field)

    csv_cols_table = []
    columns = [HEADER_FIELD, *[payslip[HEADER_FIELD] for payslip in csv_rows_table]]
    for category in categories:
        category_row = OrderedDict()
        category_row[HEADER_FIELD] = category
        for payslip in csv_rows_table:
            month = payslip[HEADER_FIELD]
            category_row[month] = payslip.get(category)
        csv_cols_table.append(category_row)

    write_payslip_csv_month_columns(columns, csv_cols_table)
    print("Done.")
