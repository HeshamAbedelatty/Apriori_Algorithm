import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
from collections import Counter

candidates = Counter()

transaction_items = {}  # Global variable to store transaction items


def read_data():
    global transaction_items  # Access the global variable
    # Open file dialog to select CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    # Read the CSV file
    bakery_data = pd.read_csv(file_path)

    # Calculate the total number of rows in the file
    total_rows = len(bakery_data)

    # Calculate the number of rows to read based on the selected percentage
    selected_percentage = float(percentage_entry.get()) / 100
    nrows_to_read = int(total_rows * selected_percentage)

    # Read only the selected percentage of rows from the CSV file
    bakery_data = pd.read_csv(file_path, usecols=['TransactionNo', 'Items'], nrows=nrows_to_read)

    # Create a dictionary to store unique items for each transaction ID
    transaction_items = {}

    # Iterate through each row in the dataframe
    for index, row in bakery_data.iterrows():
        # Extract the transaction ID and item
        tid = row['TransactionNo']
        item = row['Items']

        # If the transaction ID is not already in the dictionary, initialize it with an empty list
        if tid not in transaction_items:
            transaction_items[tid] = set()  # Initialize as a set to automatically remove duplicates

        # Add the item to the set of items for the transaction ID
        transaction_items[tid].add(item)

    # Convert the dictionary values from sets to lists
    transaction_items = {tid: list(items) for tid, items in transaction_items.items()}

    # Update the treeview with the transaction items and get the number of unique transactions
    num_unique_transactions = update_treeview(transaction_items)

    # Update the label with the number of unique transactions
    unique_transactions_label.config(text=f"Number of Unique Transactions: {num_unique_transactions}")


def update_treeview(data):
    # Clear existing items in the treeview
    for row in tree.get_children():
        tree.delete(row)

    # Insert new items into the treeview
    for tid, items in data.items():
        tree.insert("", "end", values=(tid, ", ".join(items)))
    return len(data)


def calculate_frequent_itemsets():
    global transaction_items  # Access the global variable
    if not transaction_items:
        return  # If data is not loaded, do nothing

    # Perform Apriori algorithm
    perform_apriori(transaction_items)


def perform_apriori(transaction_items):
    # Calculate the number of transactions
    num_transactions = len(transaction_items)

    # Collect all items in DataSet
    all_items = []
    for i, items in transaction_items.items():
        for j in items:
            if j not in all_items:
                all_items.append(j)

    # Get all unique items
    # all_items = [item for items in transaction_items.values() for item in items]

    # Calculate minimum support count
    # min_support = float(min_support_entry.get()) / 100
    # min_support_count = float(min_support * num_transactions)
    min_support_count = float(min_support_entry.get())
    Min_Support_label.config(text=f"Min Support: {min_support_count}")
    # Initialize candidates
    # candidates = Counter()

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

    # Output frequent item sets
    frequent_item_sets_label.config(text="Frequent Item Sets:", foreground="blue", font=("Arial", 12, "bold"))
    frequent_item_sets_text.delete(1.0, tk.END)
    for i in pl:
        frequent_item_sets_text.insert(tk.END, f"{list(i)}: {pl[i]}\n", "info")

    # Generate association rules
    generate_association_rules(pl)


def generate_association_rules(pl):
    global association_rules
    association_rules = []
    for index in pl.keys():  # rule is S = (F-S) like I1 ==> I2, I5    then Result = sup_count(I1,I2,I5)/ sup_count(I1)
        rules = []
        for item in index:
            F = index - frozenset([item])
            S = frozenset([item])
            rules.append((S, F))
            rules.append((F, S))
        association_rules.extend(rules)


def calculate_confidence(Rule):
    s, f = Rule
    S_support = candidates[s]  # S = I1 rule is S = (F-S) like I1 ==> I2, I5
    full_rule_support = candidates[s.union(f)]  # sup_count(I1,I2,I5)
    confidence = full_rule_support / S_support
    return confidence


def display_strong_rules():
    global association_rules
    if not association_rules:
        return
    # Calculate confidence for association rules
    strong_association_rules = []
    for rule in association_rules:
        s, f = rule
        if s != frozenset() and calculate_confidence(rule) >= float(min_confidence_entry.get()) / 100:
            strong_association_rules.append(rule)

    # Display strong association rules and confidence
    strong_rules_text.delete(1.0, tk.END)
    strong_rules_text.insert(tk.END, "Strong Association Rules:\n", "header")
    for rule in strong_association_rules:
        s, f = rule
        if f != frozenset():
            strong_rules_text.insert(tk.END, f"{list(s)} -> {list(f)} (Confidence: {calculate_confidence(rule):.2f})\n",
                                 "info")
    # candidates = Counter()
# Create the main window
root = tk.Tk()
root.title("Association Rule Mining")
root.geometry("800x600")

# Add a scrollbar to the main window
main_scrollbar = ttk.Scrollbar(root)
main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a canvas to contain the window contents
canvas = tk.Canvas(root, yscrollcommand=main_scrollbar.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Link the scrollbar to the canvas
main_scrollbar.config(command=canvas.yview)

# Create a frame to contain the window contents
main_frame = tk.Frame(canvas)
main_frame.pack(fill=tk.BOTH, expand=True)

# Add the frame to the canvas
canvas.create_window(0, 0, anchor=tk.NW, window=main_frame)

# Configure canvas scrolling
canvas.configure(yscrollcommand=main_scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Define style for text
style = ttk.Style()
style.configure("info.TLabel", foreground="black")
style.configure("header.TLabel", foreground="blue")

percentage_label = ttk.Label(main_frame, text="Mining In Bakery Data", font=("Arial", 20))
percentage_label.pack(pady=5)

# Add a label and entry for selecting the percentage
percentage_label = ttk.Label(main_frame, text="Select Percentage:", font=("Arial", 10))
percentage_label.pack(pady=5)
percentage_entry = ttk.Entry(main_frame)
percentage_entry.pack(pady=5)

# Add a label and entry for minimum support
min_support_label = ttk.Label(main_frame, text="Enter Minimum Support:", font=("Arial", 10))
min_support_label.pack(pady=5)
min_support_entry = ttk.Entry(main_frame)
min_support_entry.pack(pady=5)

# Add a label and entry for minimum confidence
min_confidence_label = ttk.Label(main_frame, text="Enter Minimum Confidence (%):", font=("Arial", 10))
min_confidence_label.pack(pady=5)
min_confidence_entry = ttk.Entry(main_frame)
min_confidence_entry.pack(pady=5)

# Add a button to read the data
read_button = ttk.Button(main_frame, text="Read Data", command=read_data)
read_button.pack(pady=10)

# Create a frame for treeview with scrollbar
treeview_frame = ttk.Frame(main_frame)
treeview_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a scrollbar for treeview
treeview_scroll = ttk.Scrollbar(treeview_frame)
treeview_scroll.pack(side="right", fill="y")

# Create a treeview to display the data
tree = ttk.Treeview(treeview_frame, columns=("TransactionNo", "Items"), show="headings",
                    yscrollcommand=treeview_scroll.set)
tree.heading("TransactionNo", text="TransactionNo")
tree.heading("Items", text="Items")
tree.pack(side="left", fill="both", expand=True)

# Configure the scrollbar to scroll the treeview
treeview_scroll.config(command=tree.yview)

# Add a label to display the number of unique transactions
unique_transactions_label = ttk.Label(main_frame, text="", font=("Arial", 10))
unique_transactions_label.pack(pady=5)

# Add a button to calculate frequent item sets
calculate_button = ttk.Button(main_frame, text="Calculate Frequent Item Sets", command=calculate_frequent_itemsets)
calculate_button.pack(pady=10)

# Add a label to display frequent item sets
frequent_item_sets_label = ttk.Label(main_frame, text="", font=("Arial", 10))
frequent_item_sets_label.pack(pady=5)

# Add a label to display the Min Support Count
Min_Support_label = ttk.Label(main_frame, text="", font=("Arial", 10))
Min_Support_label.pack(pady=5)

# Create a frame for frequent item sets text box with scrollbar
frequent_item_sets_frame = ttk.Frame(main_frame)
frequent_item_sets_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a scrollbar for frequent item sets text box
frequent_item_sets_scroll = ttk.Scrollbar(frequent_item_sets_frame)
frequent_item_sets_scroll.pack(side="right", fill="y")

# Add a text box to display frequent item sets
frequent_item_sets_text = tk.Text(frequent_item_sets_frame, height=10, width=100,
                                  yscrollcommand=frequent_item_sets_scroll.set, font=("Arial", 10))
frequent_item_sets_text.pack(side="left", fill="both", expand=True)

# Configure the scrollbar to scroll the text box
frequent_item_sets_scroll.config(command=frequent_item_sets_text.yview)

# # Add a button to calculate frequent item sets
# calculate_button = ttk.Button(main_frame, text="Calculate Frequent Item Sets", command=calculate_frequent_itemsets)
# calculate_button.pack(pady=10)

# Add a button to display strong association rules
display_strong_rules_button = ttk.Button(main_frame, text="Display Strong Rules", command=display_strong_rules)
display_strong_rules_button.pack(pady=10)

# Create a frame for strong association rules text box with scrollbar
strong_rules_frame = ttk.Frame(main_frame)
strong_rules_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a scrollbar for strong association rules text box
strong_rules_scroll = ttk.Scrollbar(strong_rules_frame)
strong_rules_scroll.pack(side="right", fill="y")

# Add a text box to display strong association rules
strong_rules_text = tk.Text(strong_rules_frame, height=10, width=100, yscrollcommand=strong_rules_scroll.set,
                            font=("Arial", 10))
strong_rules_text.pack(side="left", fill="both", expand=True)

# Configure the scrollbar to scroll the text box
strong_rules_scroll.config(command=strong_rules_text.yview)

# Run the main event loop
root.mainloop()
