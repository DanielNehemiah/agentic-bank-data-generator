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