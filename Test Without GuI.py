import pandas as pd
from collections import Counter

# Calculate the total number of rows in the file
total_rows = sum(1 for _ in open("Bakery.csv"))

# Calculate the number of rows to read (70% of total rows)
nrows_to_read = int(total_rows * 1.0)

# Read only the 'TransactionNo' and 'Items' columns from the CSV file
bakery_data = pd.read_csv("Bakery.csv", usecols=['TransactionNo', 'Items'], nrows=nrows_to_read)

transaction_items = {}
candidates = Counter()
numOfTransactions = 0
min_support = 50
min_confidence = 50 / 100
# Iterate through each row in the dataframe
for index, row in bakery_data.iterrows():
    # Extract the transaction ID and item
    tid = row['TransactionNo']
    item = row['Items']

    # If the transaction ID is not already in the dictionary, initialize it with an empty list
    if tid not in transaction_items:
        transaction_items[tid] = set()  # Initialize as a set to automatically remove duplicates

    # Add the item to the set of items for the transaction ID and remove duplicate
    transaction_items[tid].add(item)

# Convert the dictionary values from sets to lists
transaction_items = {tid: list(items) for tid, items in transaction_items.items()}

# Get the number of transactions
num_transactions = len(transaction_items)
print("Number OF Transactions: ", num_transactions)

# Collect all items in DataSet
all_items = []
for i, items in transaction_items.items():
    for j in items:
        if j not in all_items:
            all_items.append(j)

# min_support_count = int(min_support * num_transactions)
min_support_count = min_support
print("Min support Count: ", min_support_count)
print("Min Confidence: ", min_confidence)

c = Counter()
# Calculate the initial candidates
for i in all_items:
    for j, items in transaction_items.items():
        if i in items:
            c[i] += 1
for i in c:
    if c[i] >= min_support_count:
        candidates[frozenset([i])] += c[i]

position = 1
count = 2
pl = candidates
while True:
    candidates_test = set()
    temp = list(candidates)
    # make combination from the previous candidates
    for i in range(0, len(temp)):
        for j in range(i + 1, len(temp)):
            t = temp[i].union(temp[j])
            if len(t) == count:
                candidates_test.add(temp[i].union(temp[j]))  # like: {I1, I2}
    candidates_test = list(candidates_test)
    c = Counter()
    for i in candidates_test:
        c[i] = 0
        for j, items in transaction_items.items():
            temp = set(items)
            if i.issubset(temp):
                c[i] += 1

    l = Counter()
    for i in c:
        if c[i] >= min_support_count:  # eliminate the frequency that not fit the min_support. and put it in L
            l[i] += c[i]
            candidates[i] = c[i]

    if len(l) == 0:
        break
    pl = l
    position = count
    count += 1
print("Result: ")
print("L" + str(position) + ":")
for i in candidates:
    print(str(list(i)) + ": " + str(candidates[i]))
print()

association_rules = []
for index in pl.keys():  # rule is S = (F-S) like I1 ==> I2, I5    then Result = sup_count(I1,I2,I5)/ sup_count(I1)
    rules = []
    for item in index:
        F = index - frozenset([item])
        S = frozenset([item])
        rules.append((S, F))
        rules.append((F, S))
    association_rules.extend(rules)


# Calculate the confidence like: Result = sup_count(I1,I2,I5)/ sup_count(I1)
def calculate_confidence(Rule):
    s, f = Rule
    S_support = candidates[s]          # S = I1 rule is S = (F-S) like I1 ==> I2, I5
    full_rule_support = candidates[s.union(f)]  # sup_count(I1,I2,I5)
    confidence = full_rule_support / S_support
    return confidence


strong_association_rules = []
for rule in association_rules:
    s, f = rule
    if s != frozenset() and calculate_confidence(rule) >= min_confidence:
        strong_association_rules.append(rule)

print("Strong Association Rules:")
for rule in strong_association_rules:
    s, f = rule
    if f != frozenset():
        print(f"{list(s)} -> {list(f)} (Confidence: {calculate_confidence(rule):.2f})")
# Display the first 5 rows
# print(transaction_items[50])
# min_support_count = int(min_support * num_transactions)
# print(min_support_count)
