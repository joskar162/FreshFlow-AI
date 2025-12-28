import pandas as pd
import numpy as np
from datetime import timedelta

def load_data(filepath):
    """
    Load transaction data from CSV.

    Parameters:
    - filepath: Path to the CSV file

    Returns:
    - pd.DataFrame: Loaded data
    """
    df = pd.read_csv(filepath, parse_dates=['purchase_date'])
    return df

def feature_engineering(df, prediction_date):
    """
    Perform feature engineering for the dataset.

    Parameters:
    - df: Transaction DataFrame
    - prediction_date: Date up to which to use historical data

    Returns:
    - pd.DataFrame: Feature-engineered data
    """
    # Filter data up to prediction_date
    historical_df = df[df['purchase_date'] <= prediction_date].copy()

    # Sort by customer and date
    historical_df = historical_df.sort_values(['customer_id', 'purchase_date'])

    # Customer-level features
    customer_features = historical_df.groupby('customer_id').agg(
        total_purchases=('quantity', 'sum'),
        avg_quantity=('quantity', 'mean'),
        num_unique_products=('product_id', 'nunique'),
        last_purchase_date=('purchase_date', 'max'),
        recency_days=('purchase_date', lambda x: (prediction_date - x.max()).days)
    ).reset_index()

    # Product-level features
    product_features = historical_df.groupby('product_id').agg(
        product_total_sales=('quantity', 'sum'),
        product_avg_price=('price', 'mean'),
        product_surplus_ratio=('surplus_flag', 'mean')  # Proportion of surplus
    ).reset_index()

    # Customer-product interaction features
    interaction_features = historical_df.groupby(['customer_id', 'product_id']).agg(
        cp_total_purchases=('quantity', 'sum'),
        cp_avg_quantity=('quantity', 'mean'),
        cp_purchase_count=('quantity', 'count'),
        cp_last_purchase_date=('purchase_date', 'max'),
        cp_recency_days=('purchase_date', lambda x: (prediction_date - x.max()).days),
        cp_days_since_first=('purchase_date', lambda x: (x.max() - x.min()).days if len(x) > 1 else 0),
        cp_avg_interval=('purchase_date', lambda x: np.mean(np.diff(sorted(x))) if len(x) > 1 else 0)
    ).reset_index()

    # Seasonality: month of last purchase
    interaction_features['cp_last_month'] = interaction_features['cp_last_purchase_date'].dt.month

    # Merge features
    features = interaction_features.merge(customer_features, on='customer_id', how='left')
    features = features.merge(product_features, on='product_id', how='left')

    # Fill NaN for new customers/products
    features = features.fillna(0)

    return features

def create_labels(df, features, prediction_date, window_days):
    """
    Create labels for classification and regression.

    Parameters:
    - df: Full transaction DataFrame
    - features: Feature DataFrame
    - prediction_date: Date of prediction
    - window_days: 7 or 14 for the window

    Returns:
    - pd.DataFrame: Features with labels
    """
    future_df = df[(df['purchase_date'] > prediction_date) &
                   (df['purchase_date'] <= prediction_date + timedelta(days=window_days))]

    # Aggregate future purchases per customer-product
    future_agg = future_df.groupby(['customer_id', 'product_id']).agg(
        future_quantity=('quantity', 'sum'),
        future_purchases=('quantity', 'count')
    ).reset_index()

    # Merge with features
    labeled_features = features.merge(future_agg, on=['customer_id', 'product_id'], how='left')
    labeled_features['future_quantity'] = labeled_features['future_quantity'].fillna(0)
    labeled_features['future_purchases'] = labeled_features['future_purchases'].fillna(0)
    labeled_features['will_buy'] = (labeled_features['future_purchases'] > 0).astype(int)

    return labeled_features

def preprocess_data(filepath, prediction_date_str='2024-11-01'):
    """
    Full preprocessing pipeline.

    Parameters:
    - filepath: Path to data
    - prediction_date_str: String date for prediction cutoff

    Returns:
    - dict: Features for 7-day and 14-day predictions
    """
    df = load_data(filepath)
    prediction_date = pd.to_datetime(prediction_date_str)

    features = feature_engineering(df, prediction_date)

    # For 7-day window
    features_7d = create_labels(df, features, prediction_date, 7)
    features_7d['window'] = 7

    # For 14-day window
    features_14d = create_labels(df, features, prediction_date, 14)
    features_14d['window'] = 14

    return {'7d': features_7d, '14d': features_14d}

if __name__ == "__main__":
    # Example usage
    data = preprocess_data('harvestiq/data/transactions.csv')
    print("Preprocessing complete. Features for 7d and 14d windows generated.")