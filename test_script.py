# Broken Python script to test the agent
# This has intentional errors that the agent will fix

import pandas as pd
import numpy as np

# Error 1: Wrong column name
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Salary': [50000, 60000, 75000]
}

df = pd.DataFrame(data)

# This will fail - column is 'Name' not 'name'
print(df['Name'])

# Other operations
print(df.head())