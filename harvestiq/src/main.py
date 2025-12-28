import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.generate_data import generate_dummy_data
from src.preprocessing import preprocess_data
from src.models import HarvestIQModels
from src.recommendations import HarvestIQRecommender

def main():
    """
    Main function to run the HarvestIQ recommender system.
    """
    print("Starting HarvestIQ Recommender System...")

    # Step 1: Generate dummy data
    print("Generating dummy dataset...")
    df = generate_dummy_data()
    df.to_csv('harvestiq/data/transactions.csv', index=False)
    print("Dummy data saved.")

    # Step 2: Preprocess data
    print("Preprocessing data...")
    preprocessed = preprocess_data('harvestiq/data/transactions.csv')
    data_7d = preprocessed['7d']
    data_14d = preprocessed['14d']
    print("Preprocessing complete.")

    # Step 3: Train models
    print("Training models...")
    models = HarvestIQModels()
    models.train_classifiers(data_7d, data_14d)
    models.train_regressor(data_7d, data_14d)
    models.save_models()
    print("Models trained and saved.")

    # Step 4: Generate recommendations for a sample customer
    print("Generating recommendations...")
    recommender = HarvestIQRecommender()
    sample_customer = df['customer_id'].iloc[0]  # First customer
    prediction_date = pd.to_datetime('2024-11-01')  # Same as in preprocessing
    recommendations = recommender.recommend_for_customer(df, sample_customer, prediction_date, top_n=5)

    print(f"Top 5 recommendations for customer {sample_customer}:")
    print(recommendations)

if __name__ == "__main__":
    import pandas as pd
    main()