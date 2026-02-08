import csv

# Create a CSV with Excel-prevention artifacts
data = [
    {'name': 'Test', 'value': '="123"'},
    {'name': 'Test2', 'value': '"456"'}
]

with open('data/test_artifacts.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'value'])
    writer.writeheader()
    writer.writerows(data)
