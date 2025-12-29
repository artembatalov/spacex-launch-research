import csv
from datetime import datetime

file1 = 'from2006to2022.csv'
file2 = 'from2022to2025.csv'
output_file = 'from2006to2025.csv'


cutoff_date = datetime(2022, 10, 31)

def read_filtered_rows(filename, cutoff, before=True):
    rows = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M')
            if before:
                if row_date <= cutoff:
                    rows.append(row)
            else:
                if row_date >= cutoff:
                    rows.append(row)
    return rows


first_part = read_filtered_rows(file1, cutoff_date, before=True)
second_part = read_filtered_rows(file2, cutoff_date, before=False)


merged_rows = first_part + second_part

flight_counter = 1

for row in merged_rows:
    row['flight_number'] = str(flight_counter)
    flight_counter += 1


if merged_rows:
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=merged_rows[0].keys())
        writer.writeheader()
        writer.writerows(merged_rows)

print(f'Объединение выполнено. Итоговый файл: {output_file}')