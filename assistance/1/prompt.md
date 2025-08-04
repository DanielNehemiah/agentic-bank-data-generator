Goal: Create a langgraph agentic system to create a large dataset with customer information, KYC details, and transaction data for a fictional bank, similar to the concept of "Contoso". The fictional bank is a European leader in financial services for over 150 years, it is built on three complementary businesses: French Retail Banking, International Retail Banking and Financial Services and Global Banking and Investor Solutions. 

Steps to generate the dataset from scratch:

Step 1. Define a detailed data schema for customers, KYC data (including compliance activities like transaction monitoring, screening for PEP/Negative News/Sanctions), and transactions of each business. Create a sqlite database for this schema.
Step 2. Create the langgraph nodes to mimic real world banking data flow and add to the database created in step 1:
    - A customer is created
    - KYC details are updated
    - Customer starts getting involved in the transactions of a business
    - Customers are periodically screened with the compliance systems like negative news screening, sanctions screening
    - Transaction Data is regularly generated
    - If the customer is involved in any financial crime they are flagged and reported

Additional information on Step 2: 
Implement logic to associate transactions with customers and simulate KYC processes, potentially using:
- Statistical distributions: To mimic real-world transaction frequencies and values.
- Markov models or other techniques: To model customer behavior and transaction sequences.