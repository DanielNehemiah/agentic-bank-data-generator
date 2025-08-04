# agentic-bank-data-generator

A LangGraph agent to create synthetic data for a fictional bank. The data mimics a simple bank with tables for Customer details, KYC, Screening, Transactions

## How to run

Command to create your own fictionl bank data: 

```uv run python .\src\agentic_bank_data_generator\agentic_data_generator.py -c 15```
- The output is stored in fictional_bank.db
- Use the parameter --customers or -c to specific number of customers in the bank

## Output Tables
#### Customers
  <img width="1320" height="465" alt="image" src="https://github.com/user-attachments/assets/263a9c63-6dbe-4d16-aca4-1633fcd0d84d" />

#### Transactions
<img width="1628" height="543" alt="image" src="https://github.com/user-attachments/assets/f3fdf60e-ae51-430a-bf37-48d6a713c0f4" />

#### KYC
<img width="1032" height="459" alt="image" src="https://github.com/user-attachments/assets/ac52bc80-64e2-4746-a90c-bba437862fee" />

#### Screening Logs
<img width="1006" height="537" alt="image" src="https://github.com/user-attachments/assets/9886a3f4-7995-4844-bd2e-fcf66fd76303" />

#### FlaggedReports
<img width="866" height="167" alt="image" src="https://github.com/user-attachments/assets/560da4a0-5fc8-4c81-af16-8daf50ce79ca" />

## Code context
1. Code base started using Google Gemini 2.5 Pro
    - Details in `assistance\1` prompt.md, response.md, thinking.md
2. Aspects added
    - UV environment
    - Error in flag corrected
    - Commnand line arguments
3. Todo
    - Use an llm instead of Faker
    - Create a watchlist
