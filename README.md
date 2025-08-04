# agentic-bank-data-generator

A LangGraph agent to create synthetic data for a fictional bank. The data mimics a simple bank with tables for Customer details, KYC, Screening, Transactions

## How to run

Command to create your own fictionl bank data: 

```uv run python .\src\agentic_bank_data_generator\agentic_data_generator.py -c 15```
- The output is stored in fictional_bank.db
- Use the parameter --customers or -c to specific number of customers in the bank

## Output Sample


## Code context
1. Code base started using Google Gemini 2.5 Pro
    - Details in assistance\1 prompt.md, response.md, thinking.md
2. Aspects added
    - UV environment
    - Error in flag
    - Commnand line arguments
3. Todo
    - Use an llm instead of Faker
    - Create a watchlist
