import pandas as pd
import numpy as np
from .models import HarvestIQModels
from .preprocessing import feature_engineering

class HarvestIQRecommender:
    def __init__(self, model_path='harvestiq/models/'):
        self.models = HarvestIQModels()
        self.models.load_models(model_path)

    def generate_candidate_products(self, historical_df, customer_id, prediction_date):
        """
        Generate candidate products for a customer: all products they have bought or all products.

        For simplicity, use all products they have interacted with.

        Parameters:
        - historical_df: Historical transactions
        - customer_id: Customer to recommend for
        - prediction_date: Prediction date

        Returns:
        - pd.DataFrame: Candidate features
        """
        # Get unique products for the customer
        customer_products = historical_df[historical_df['customer_id'] == customer_id]['product_id'].unique()

        # For each product, compute features as if it's the current state
        candidate_features = []
        for prod in customer_products:
            # Filter historical for this customer-product
            cp_hist = historical_df[(historical_df['customer_id'] == customer_id) &
                                    (historical_df['product_id'] == prod) &
                                    (historical_df['purchase_date'] <= prediction_date)]

            if cp_hist.empty:
                continue  # Skip if no history

            # Compute features (simplified, reuse from preprocessing)
            features = {
                'customer_id': customer_id,
                'product_id': prod,
                'cp_total_purchases': cp_hist['quantity'].sum(),
                'cp_avg_quantity': cp_hist['quantity'].mean(),
                'cp_purchase_count': len(cp_hist),
                'cp_last_purchase_date': cp_hist['purchase_date'].max(),
                'cp_recency_days': (prediction_date - cp_hist['purchase_date'].max()).days,
                'cp_days_since_first': (cp_hist['purchase_date'].max() - cp_hist['purchase_date'].min()).days if len(cp_hist) > 1 else 0,
                'cp_avg_interval': np.mean(np.diff(sorted(cp_hist['purchase_date']))) if len(cp_hist) > 1 else 0,
                'cp_last_month': cp_hist['purchase_date'].max().month,
                # Add customer and product level (would need to compute globally)
                # For simplicity, assume we have precomputed
            }
            candidate_features.append(features)

        return pd.DataFrame(candidate_features)

    def compute_recommendation_score(self, prob_7d, prob_14d, qty_7d, qty_14d, surplus_ratio):
        """
        Compute final recommendation score.

        Score = weighted prob * predicted qty * surplus bonus

        Parameters:
        - prob_7d, prob_14d: Probabilities
        - qty_7d, qty_14d: Predicted quantities
        - surplus_ratio: Product surplus ratio

        Returns:
        - float: Score
        """
        # Weighted probability (more weight on 7d)
        weighted_prob = 0.6 * prob_7d + 0.4 * prob_14d
        # Average quantity
        avg_qty = (qty_7d + qty_14d) / 2
        # Surplus bonus: higher for surplus products
        surplus_bonus = 1 + surplus_ratio  # e.g., 1.2 if 20% surplus

        score = weighted_prob * avg_qty * surplus_bonus
        return score

    def recommend_for_customer(self, historical_df, customer_id, prediction_date, top_n=10):
        """
        Generate top-N recommendations for a customer.

        Parameters:
        - historical_df: Full historical data
        - customer_id: Customer ID
        - prediction_date: Date for prediction
        - top_n: Number of recommendations

        Returns:
        - pd.DataFrame: Top recommendations with scores
        """
        candidates = self.generate_candidate_products(historical_df, customer_id, prediction_date)

        if candidates.empty:
            return pd.DataFrame()

        # Predict for 7d and 14d
        prob_7d, qty_7d = self.models.predict(candidates, 7)
        prob_14d, qty_14d = self.models.predict(candidates, 14)

        # Assume surplus_ratio is available (from preprocessing)
        # For now, dummy, but in real, merge from product_features
        candidates['surplus_ratio'] = 0.2  # Placeholder

        # Compute scores
        scores = []
        for i in range(len(candidates)):
            score = self.compute_recommendation_score(
                prob_7d[i], prob_14d[i], qty_7d[i], qty_14d[i], candidates.iloc[i]['surplus_ratio']
            )
            scores.append(score)

        candidates['score'] = scores
        candidates['prob_7d'] = prob_7d
        candidates['prob_14d'] = prob_14d
        candidates['qty_7d'] = qty_7d
        candidates['qty_14d'] = qty_14d

        # Sort by score descending
        recommendations = candidates.sort_values('score', ascending=False).head(top_n)

        return recommendations[['customer_id', 'product_id', 'score', 'prob_7d', 'prob_14d', 'qty_7d', 'qty_14d']]

if __name__ == "__main__":
    # Example usage
    recommender = HarvestIQRecommender()
    print("Recommender loaded. Use recommend_for_customer method.")