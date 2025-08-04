Of course. Here's a complete, end-to-end solution for creating a synthetic banking dataset using a LangGraph agentic system. This system will simulate the data lifecycle for a fictional European bank, "OmniBanque," covering customer creation, KYC processes, and transaction generation.

### Step 1: Data Schema and Database Creation

First, we'll define a robust schema and create the corresponding SQLite database. The schema is designed to capture the complexity of a modern financial institution with distinct business lines.

The fictional bank, **OmniBanque**, has three core businesses:

1.  **French Retail Banking (FRB)**
2.  **International Retail Banking and Financial Services (IRFS)**
3.  **Global Banking and Investor Solutions (GBIS)**

#### Database Schema (`schema.py`)

This script defines the structure of our database tables.

```python
import sqlite3

def create_database(db_name="fictional_bank.db"):
    """Creates the SQLite database and tables for OmniBanque."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # ## Customer Table
    # Stores core information about each customer.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID TEXT PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        DateOfBirth DATE NOT NULL,
        Nationality TEXT NOT NULL,
        CountryOfResidence TEXT NOT NULL,
        PrimaryBusinessLine TEXT CHECK(PrimaryBusinessLine IN ('FRB', 'IRFS', 'GBIS')),
        CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # ## KYC (Know Your Customer) Table
    # Stores compliance and identity verification data.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS KYC (
        KycID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID TEXT UNIQUE,
        RiskLevel TEXT CHECK(RiskLevel IN ('Low', 'Medium', 'High')) NOT NULL,
        IdentityVerified BOOLEAN NOT NULL,
        AddressVerified BOOLEAN NOT NULL,
        LastScreeningDate DATE,
        IsFlagged BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
    );
    ''')

    # ## Screening Log Table
    # Logs all compliance screening activities.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ScreeningLogs (
        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID TEXT,
        ScreeningType TEXT CHECK(ScreeningType IN ('Sanctions', 'PEP', 'NegativeNews')),
        ScreeningDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Result TEXT CHECK(Result IN ('Clear', 'Hit', 'Potential Match')),
        Details TEXT,
        FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
    );
    ''')

    # ## Transactions Table
    # Records all financial transactions for customers.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        TransactionID TEXT PRIMARY KEY,
        CustomerID TEXT,
        TransactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Amount REAL NOT NULL,
        Currency TEXT NOT NULL DEFAULT 'EUR',
        TransactionType TEXT, -- e.g., 'Deposit', 'Withdrawal', 'Transfer', 'Investment'
        BusinessLine TEXT CHECK(BusinessLine IN ('FRB', 'IRFS', 'GBIS')),
        Description TEXT,
        IsSuspicious BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
    );
    ''')

    # ## Flagged Reports Table
    # A dedicated table for customers who are flagged for financial crime.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FlaggedReports (
        ReportID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID TEXT,
        FlagDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Reason TEXT, -- e.g., 'Sanction Hit', 'Suspicious Transaction Pattern'
        ReportedToAuthorities BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
    );
    ''')

    print("Database and tables created successfully. 🏦")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
```

-----

### Step 2: LangGraph Agentic System

Now, we'll build the agentic workflow using LangGraph. This system will simulate the real-world processes of a bank, from onboarding a customer to monitoring their transactions.

#### Installation

First, ensure you have the necessary libraries installed:

```bash
pip install langgraph faker numpy
```

#### The Agentic System (`agentic_data_generator.py`)

This script contains the full logic for the LangGraph nodes and the graph itself. It uses `Faker` to generate realistic data, `numpy` for statistical distributions, and a simple Markov model for transaction sequences.

```python
import sqlite3
import uuid
import random
import datetime
from faker import Faker
import numpy as np
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# --- Configuration ---
DB_NAME = "fictional_bank.db"
BUSINESS_LINES = ['FRB', 'IRFS', 'GBIS']
RISK_LEVELS = ['Low', 'Medium', 'High']
SCREENING_TYPES = ['Sanctions', 'PEP', 'NegativeNews']
TRANSACTION_TYPES = {
    'FRB': ['Deposit', 'Withdrawal', 'Card Payment', 'Loan Repayment'],
    'IRFS': ['International Transfer', 'Currency Exchange', 'Card Payment'],
    'GBIS': ['Securities Trade', 'Bond Purchase', 'Derivatives Trade', 'Asset Management Fee']
}
# Markov Chain for transaction types (simple transition probabilities)
TRANSITION_MATRIX = {
    'start': {'Deposit': 0.4, 'International Transfer': 0.3, 'Securities Trade': 0.3},
    'Deposit': {'Withdrawal': 0.5, 'Card Payment': 0.5},
    'Withdrawal': {'Deposit': 0.3, 'Card Payment': 0.7},
    'Card Payment': {'Card Payment': 0.6, 'Deposit': 0.2, 'Withdrawal': 0.2},
    'International Transfer': {'Currency Exchange': 0.8, 'Card Payment': 0.2},
    'Currency Exchange': {'International Transfer': 0.5, 'Securities Trade': 0.5},
    'Securities Trade': {'Bond Purchase': 0.6, 'Derivatives Trade': 0.3, 'Asset Management Fee': 0.1},
    'Bond Purchase': {'Securities Trade': 0.7, 'Asset Management Fee': 0.3},
    'Derivatives Trade': {'Securities Trade': 0.9, 'Asset Management Fee': 0.1},
    'Loan Repayment': {'Card Payment': 1.0},
    'Asset Management Fee': {'Securities Trade': 1.0}
}
# Initialize Faker for European data
fake = Faker('en_GB')

# --- Agent State ---
class AgentState(TypedDict):
    customer_id: str
    business_line: str
    risk_level: str
    transaction_count: int
    current_date: datetime.date
    last_transaction_type: str
    is_flagged: bool = False
    run_history: List[str]

# --- Database Helper Functions ---
def db_execute(query, params=(), fetch=None):
    """A utility function to interact with the SQLite database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetch == 'one':
            return cursor.fetchone()
        if fetch == 'all':
            return cursor.fetchall()
        return cursor.lastrowid

# --- LangGraph Nodes ---

def create_customer_node(state: AgentState):
    """Node 1: Onboards a new customer."""
    print("Executing Node: create_customer_node 🧍")
    business_line = random.choice(BUSINESS_LINES)
    customer = {
        "CustomerID": str(uuid.uuid4()),
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "DateOfBirth": fake.date_of_birth(minimum_age=18, maximum_age=90),
        "Nationality": fake.country(),
        "CountryOfResidence": "France" if business_line == 'FRB' else fake.country(),
        "PrimaryBusinessLine": business_line
    }
    db_execute(
        "INSERT INTO Customers VALUES (:CustomerID, :FirstName, :LastName, :DateOfBirth, :Nationality, :CountryOfResidence, :PrimaryBusinessLine, CURRENT_TIMESTAMP)",
        customer
    )
    state['customer_id'] = customer['CustomerID']
    state['business_line'] = customer['PrimaryBusinessLine']
    state['current_date'] = datetime.date.today() - datetime.timedelta(days=random.randint(365, 1825))
    state['run_history'].append("CustomerCreated")
    return state

def update_kyc_node(state: AgentState):
    """Node 2: Completes KYC, assigns risk, and performs initial screening."""
    print("Executing Node: update_kyc_node 📝")
    risk_level = random.choices(RISK_LEVELS, weights=[0.6, 0.3, 0.1], k=1)[0]
    kyc_data = {
        "CustomerID": state['customer_id'],
        "RiskLevel": risk_level,
        "IdentityVerified": True,
        "AddressVerified": True,
        "LastScreeningDate": state['current_date']
    }
    db_execute(
        "INSERT INTO KYC (CustomerID, RiskLevel, IdentityVerified, AddressVerified, LastScreeningDate) VALUES (?, ?, ?, ?, ?)",
        (kyc_data['CustomerID'], kyc_data['RiskLevel'], kyc_data['IdentityVerified'], kyc_data['AddressVerified'], kyc_data['LastScreeningDate'])
    )
    # Initial screening
    for screen_type in SCREENING_TYPES:
        db_execute(
            "INSERT INTO ScreeningLogs (CustomerID, ScreeningType, Result, Details) VALUES (?, ?, 'Clear', 'Initial onboarding screening.')",
            (state['customer_id'], screen_type)
        )
    state['risk_level'] = risk_level
    state['last_transaction_type'] = 'start'
    state['run_history'].append("KYCUpdated")
    return state

def generate_transactions_node(state: AgentState):
    """Node 3: Generates a batch of transactions for the customer."""
    print("Executing Node: generate_transactions_node 💳")
    customer_id = state['customer_id']
    business_line = state['business_line']
    risk_level = state['risk_level']
    
    # Use Poisson distribution to determine number of transactions in a period
    num_transactions = np.random.poisson(lam=5 if risk_level == 'Low' else (10 if risk_level == 'Medium' else 20))

    for _ in range(num_transactions):
        state['current_date'] += datetime.timedelta(days=random.randint(1, 30))
        
        # Use Markov Chain to determine next transaction type
        possible_next_transactions = list(TRANSITION_MATRIX[state['last_transaction_type']].keys())
        probabilities = list(TRANSITION_MATRIX[state['last_transaction_type']].values())
        transaction_type = random.choices(possible_next_transactions, weights=probabilities, k=1)[0]
        state['last_transaction_type'] = transaction_type

        # Use log-normal distribution for more realistic transaction amounts
        if business_line == 'GBIS':
            amount = round(np.random.lognormal(mean=10, sigma=1.5), 2) # Larger amounts for investment banking
        else:
            amount = round(np.random.lognormal(mean=5, sigma=1.0), 2)
            
        is_suspicious = (amount > 50000 and risk_level != 'High') # Simple rule for suspicion
        
        transaction_data = {
            "TransactionID": str(uuid.uuid4()),
            "CustomerID": customer_id,
            "TransactionDate": state['current_date'],
            "Amount": amount,
            "TransactionType": transaction_type,
            "BusinessLine": business_line,
            "Description": f"{transaction_type} via OmniBanque {business_line}",
            "IsSuspicious": is_suspicious
        }
        db_execute(
            "INSERT INTO Transactions (TransactionID, CustomerID, TransactionDate, Amount, TransactionType, BusinessLine, Description, IsSuspicious) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            list(transaction_data.values())
        )
        if is_suspicious:
            state['is_flagged'] = True
            db_execute("UPDATE KYC SET IsFlagged = TRUE WHERE CustomerID = ?", (customer_id,))

    state['transaction_count'] = state.get('transaction_count', 0) + num_transactions
    state['run_history'].append(f"Generated {num_transactions} transactions")
    return state

def periodic_screening_node(state: AgentState):
    """Node 4: Simulates periodic compliance screenings."""
    print("Executing Node: periodic_screening_node 🔍")
    # Simulate a small chance of a "hit" during screening
    hit_chance = 0.01 if state['risk_level'] == 'High' else 0.001
    result = 'Clear'
    details = 'Routine periodic screening.'
    
    if random.random() < hit_chance:
        result = 'Hit'
        details = 'Match found against sanctions list during routine check.'
        state['is_flagged'] = True
        db_execute("UPDATE KYC SET IsFlagged = TRUE WHERE CustomerID = ?", (state['customer_id'],))

    # Log the screening activity
    screen_type = random.choice(SCREENING_TYPES)
    db_execute(
        "INSERT INTO ScreeningLogs (CustomerID, ScreeningType, Result, Details) VALUES (?, ?, ?, ?)",
        (state['customer_id'], screen_type, result, details)
    )
    db_execute("UPDATE KYC SET LastScreeningDate = ? WHERE CustomerID = ?", (state['current_date'], state['customer_id']))
    
    state['run_history'].append(f"ScreeningPerformed: {result}")
    return state

def flag_customer_node(state: AgentState):
    """Node 5: Creates a formal report for a flagged customer."""
    print("Executing Node: flag_customer_node 🚩")
    reason = "Suspicious Transaction Pattern" if not any("Hit" in s for s in state['run_history'][-2:]) else "Sanction Hit"
    db_execute(
        "INSERT INTO FlaggedReports (CustomerID, Reason) VALUES (?, ?)",
        (state['customer_id'], reason)
    )
    state['run_history'].append("CustomerFlagged")
    return state
    
# --- Graph Logic ---

def should_continue(state: AgentState):
    """Conditional Edge: Decide whether to continue generating data or end."""
    if state['is_flagged']:
        return "flag_customer"
    # Simulate for roughly 5 years of activity
    if state.get('transaction_count', 0) > 240: # Avg 4 transactions/month for 5 years
        return "end"
    return "continue_simulation"

# --- Build and Run the Graph ---

def build_graph():
    """Builds the LangGraph agent."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("create_customer", create_customer_node)
    workflow.add_node("update_kyc", update_kyc_node)
    workflow.add_node("generate_transactions", generate_transactions_node)
    workflow.add_node("periodic_screening", periodic_screening_node)
    workflow.add_node("flag_customer", flag_customer_node)
    
    # Set entry point
    workflow.set_entry_point("create_customer")
    
    # Add edges
    workflow.add_edge("create_customer", "update_kyc")
    workflow.add_edge("update_kyc", "generate_transactions")
    workflow.add_edge("periodic_screening", "generate_transactions")
    workflow.add_edge("flag_customer", END)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "generate_transactions",
        should_continue,
        {
            "continue_simulation": "periodic_screening",
            "flag_customer": "flag_customer",
            "end": END
        }
    )
    
    return workflow.compile()

def run_simulation(num_customers=100):
    """Runs the full data generation simulation."""
    # Step 1: Create the database from schema.py
    from schema import create_database
    create_database(DB_NAME)
    
    # Step 2: Build the agentic graph
    app = build_graph()
    
    # Step 3: Run the simulation for each customer
    for i in range(num_customers):
        print(f"\n--- Generating data for customer {i+1}/{num_customers} ---")
        initial_state = {"run_history": []}
        app.invoke(initial_state)
    
    print(f"\n✅ Simulation complete. {num_customers} customer profiles generated in '{DB_NAME}'.")


if __name__ == "__main__":
    # Generate data for 500 customers
    run_simulation(num_customers=500)

```

### How to Run the System

1.  **Save the Files**: Save the two Python code blocks above as `schema.py` and `agentic_data_generator.py` in the same directory.
2.  **Run the Generator**: Open your terminal, navigate to the directory, and run the main script:
    ```bash
    python agentic_data_generator.py
    ```

### Output

After the script finishes, you will find a file named **`fictional_bank.db`** in the same directory. This SQLite database contains the generated data, which you can explore using any database tool like DB Browser for SQLite.

The output in your terminal will look something like this, showing the agent's progress for each customer:

```
Database and tables created successfully. 🏦

--- Generating data for customer 1/500 ---
Executing Node: create_customer_node 🧍
Executing Node: update_kyc_node 📝
Executing Node: generate_transactions_node 💳
Executing Node: periodic_screening_node 🔍
Executing Node: generate_transactions_node 💳
...
Executing Node: generate_transactions_node 💳
Executing Node: flag_customer_node 🚩

--- Generating data for customer 2/500 ---
Executing Node: create_customer_node 🧍
...
```

This system successfully creates a rich, interconnected dataset by modeling the real-world flow of banking operations, from customer onboarding to ongoing monitoring, using an agentic architecture. The use of statistical methods ensures the data has a realistic distribution and complexity.