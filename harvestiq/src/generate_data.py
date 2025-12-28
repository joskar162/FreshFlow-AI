import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_data(num_customers=1000, num_products=50, num_transactions=10000):
    """
    Generate a dummy dataset for HarvestIQ recommender system.

    Parameters:
    - num_customers: Number of unique customers
    - num_products: Number of unique products
    - num_transactions: Total number of transactions

    Returns:
    - pd.DataFrame: Dummy transaction data
    """
    np.random.seed(42)  # For reproducibility

    # Generate customer IDs
    customers = [f'CUST_{i:04d}' for i in range(1, num_customers + 1)]

    # Generate product IDs and categories
    products = [f'PROD_{i:03d}' for i in range(1, num_products + 1)]
    categories = ['Fruits', 'Vegetables', 'Herbs', 'Leafy Greens']
    product_categories = np.random.choice(categories, num_products)

    # Generate transactions
    data = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)

    for _ in range(num_transactions):
        customer_id = np.random.choice(customers)
        product_id = np.random.choice(products)
        product_category = product_categories[int(product_id.split('_')[1]) - 1]  # Map product to category
        purchase_date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
        quantity = np.random.poisson(2) + 1  # Poisson distribution for quantity, min 1
        price = np.random.uniform(1.0, 10.0)  # Random price between 1 and 10
        surplus_flag = np.random.choice([0, 1], p=[0.8, 0.2])  # 20% chance of surplus
        month = purchase_date.month  # Use month for seasonality

        data.append({
            'customer_id': customer_id,
            'product_id': product_id,
            'product_category': product_category,
            'purchase_date': purchase_date.date(),
            'quantity': quantity,
            'price': price,
            'surplus_flag': surplus_flag,
            'month': month
        })

    df = pd.DataFrame(data)
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])  # Ensure datetime
    return df

if __name__ == "__main__":
    # Generate and save dummy data
    df = generate_dummy_data()
    df.to_csv('harvestiq/data/transactions.csv', index=False)
    print("Dummy dataset generated and saved to harvestiq/data/transactions.csv")