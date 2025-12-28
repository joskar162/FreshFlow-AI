import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, mean_absolute_error
import joblib
import os

# Copy from generate_data.py
def generate_dummy_data(num_customers=1000, num_products=50, num_transactions=10000):
    np.random.seed(42)
    customers = [f'CUST_{i:04d}' for i in range(1, num_customers + 1)]
    products = [f'PROD_{i:03d}' for i in range(1, num_products + 1)]
    categories = ['Fruits', 'Vegetables', 'Herbs', 'Leafy Greens']
    product_categories = np.random.choice(categories, num_products)
    data = []
    start_date = pd.to_datetime('2023-01-01')
    end_date = pd.to_datetime('2024-12-31')
    for _ in range(num_transactions):
        customer_id = np.random.choice(customers)
        product_id = np.random.choice(products)
        product_category = product_categories[int(product_id.split('_')[1]) - 1]
        purchase_date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
        quantity = np.random.poisson(2) + 1
        price = np.random.uniform(1.0, 10.0)
        surplus_flag = np.random.choice([0, 1], p=[0.8, 0.2])
        month = purchase_date.month
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
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    return df

# Copy preprocessing functions
def load_data(filepath):
    df = pd.read_csv(filepath, parse_dates=['purchase_date'])
    return df

def feature_engineering(df, prediction_date):
    historical_df = df[df['purchase_date'] <= prediction_date].copy()
    historical_df = historical_df.sort_values(['customer_id', 'purchase_date'])
    customer_features = historical_df.groupby('customer_id').agg(
        total_purchases=('quantity', 'sum'),
        avg_quantity=('quantity', 'mean'),
        num_unique_products=('product_id', 'nunique'),
        last_purchase_date=('purchase_date', 'max'),
        recency_days=('purchase_date', lambda x: (prediction_date - x.max()).days)
    ).reset_index()
    product_features = historical_df.groupby('product_id').agg(
        product_total_sales=('quantity', 'sum'),
        product_avg_price=('price', 'mean'),
        product_surplus_ratio=('surplus_flag', 'mean')
    ).reset_index()
    interaction_features = historical_df.groupby(['customer_id', 'product_id']).agg(
        cp_total_purchases=('quantity', 'sum'),
        cp_avg_quantity=('quantity', 'mean'),
        cp_purchase_count=('quantity', 'count'),
        cp_last_purchase_date=('purchase_date', 'max'),
        cp_recency_days=('purchase_date', lambda x: (prediction_date - x.max()).days),
        cp_days_since_first=('purchase_date', lambda x: (x.max() - x.min()).days if len(x) > 1 else 0),
        cp_avg_interval=('purchase_date', lambda x: np.mean(np.diff(sorted(x))) if len(x) > 1 else 0)
    ).reset_index()
    interaction_features['cp_last_month'] = interaction_features['cp_last_purchase_date'].dt.month
    features = interaction_features.merge(customer_features, on='customer_id', how='left')
    features = features.merge(product_features, on='product_id', how='left')
    features = features.fillna(0)
    return features

def create_labels(df, features, prediction_date, window_days):
    future_df = df[(df['purchase_date'] > prediction_date) &
                   (df['purchase_date'] <= prediction_date + timedelta(days=window_days))]
    future_agg = future_df.groupby(['customer_id', 'product_id']).agg(
        future_quantity=('quantity', 'sum'),
        future_purchases=('quantity', 'count')
    ).reset_index()
    labeled_features = features.merge(future_agg, on=['customer_id', 'product_id'], how='left')
    labeled_features['future_quantity'] = labeled_features['future_quantity'].fillna(0)
    labeled_features['future_purchases'] = labeled_features['future_purchases'].fillna(0)
    labeled_features['will_buy'] = (labeled_features['future_purchases'] > 0).astype(int)
    return labeled_features

def preprocess_data(filepath, prediction_date_str='2024-11-01'):
    df = load_data(filepath)
    prediction_date = pd.to_datetime(prediction_date_str)
    features = feature_engineering(df, prediction_date)
    features_7d = create_labels(df, features, prediction_date, 7)
    features_7d['window'] = 7
    features_14d = create_labels(df, features, prediction_date, 14)
    features_14d['window'] = 14
    return {'7d': features_7d, '14d': features_14d}

# Copy models class
class HarvestIQModels:
    def __init__(self):
        self.classifier_7d = RandomForestClassifier(n_estimators=100, random_state=42)
        self.classifier_14d = RandomForestClassifier(n_estimators=100, random_state=42)
        self.regressor = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_features(self, df):
        drop_cols = ['customer_id', 'product_id', 'cp_last_purchase_date', 'last_purchase_date',
                     'future_quantity', 'future_purchases', 'will_buy', 'window']
        X = df.drop(columns=drop_cols, errors='ignore')
        y_class = df['will_buy']
        y_reg = df[df['will_buy'] == 1]['future_quantity']
        return X, y_class, y_reg

    def train_classifiers(self, data_7d, data_14d):
        X_7d, y_7d, _ = self.prepare_features(data_7d)
        X_train_7d, X_test_7d, y_train_7d, y_test_7d = train_test_split(X_7d, y_7d, test_size=0.2, random_state=42)
        self.classifier_7d.fit(X_train_7d, y_train_7d)
        y_pred_proba_7d = self.classifier_7d.predict_proba(X_test_7d)[:, 1]
        auc_7d = roc_auc_score(y_test_7d, y_pred_proba_7d)
        print(f"7-day Classifier AUC: {auc_7d:.4f}")
        X_14d, y_14d, _ = self.prepare_features(data_14d)
        X_train_14d, X_test_14d, y_train_14d, y_test_14d = train_test_split(X_14d, y_14d, test_size=0.2, random_state=42)
        self.classifier_14d.fit(X_train_14d, y_train_14d)
        y_pred_proba_14d = self.classifier_14d.predict_proba(X_test_14d)[:, 1]
        auc_14d = roc_auc_score(y_test_14d, y_pred_proba_14d)
        print(f"14-day Classifier AUC: {auc_14d:.4f}")

    def train_regressor(self, data_7d, data_14d):
        pos_7d = data_7d[data_7d['will_buy'] == 1]
        pos_14d = data_14d[data_14d['will_buy'] == 1]
        pos_data = pd.concat([pos_7d, pos_14d])
        X_reg, _, y_reg = self.prepare_features(pos_data)
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
        self.regressor.fit(X_train_reg, y_train_reg)
        y_pred_reg = self.regressor.predict(X_test_reg)
        mae = mean_absolute_error(y_test_reg, y_pred_reg)
        print(f"Regressor MAE: {mae:.4f}")

    def predict(self, features_df, window):
        X = features_df.drop(columns=['customer_id', 'product_id', 'cp_last_purchase_date', 'last_purchase_date'], errors='ignore')
        if window == 7:
            prob = self.classifier_7d.predict_proba(X)[:, 1]
        elif window == 14:
            prob = self.classifier_14d.predict_proba(X)[:, 1]
        else:
            raise ValueError("Window must be 7 or 14")
        qty = self.regressor.predict(X)
        return prob, qty

    def save_models(self, path='harvestiq/models/'):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.classifier_7d, f'{path}classifier_7d.pkl')
        joblib.dump(self.classifier_14d, f'{path}classifier_14d.pkl')
        joblib.dump(self.regressor, f'{path}regressor.pkl')

    def load_models(self, path='harvestiq/models/'):
        self.classifier_7d = joblib.load(f'{path}classifier_7d.pkl')
        self.classifier_14d = joblib.load(f'{path}classifier_14d.pkl')
        self.regressor = joblib.load(f'{path}regressor.pkl')

# Copy recommender class
class HarvestIQRecommender:
    def __init__(self, model_path='harvestiq/models/'):
        self.models = HarvestIQModels()
        self.models.load_models(model_path)

    def generate_candidate_products(self, historical_df, customer_id, prediction_date):
        customer_products = historical_df[historical_df['customer_id'] == customer_id]['product_id'].unique()
        candidate_features = []
        # Compute global customer features
        cust_hist = historical_df[(historical_df['customer_id'] == customer_id) & (historical_df['purchase_date'] <= prediction_date)]
        if cust_hist.empty:
            return pd.DataFrame()
        customer_features = {
            'total_purchases': cust_hist['quantity'].sum(),
            'avg_quantity': cust_hist['quantity'].mean(),
            'num_unique_products': cust_hist['product_id'].nunique(),
            'last_purchase_date': cust_hist['purchase_date'].max(),
            'recency_days': (prediction_date - cust_hist['purchase_date'].max()).days
        }
        # Compute global product features
        product_features = {}
        for prod in customer_products:
            prod_hist = historical_df[(historical_df['product_id'] == prod) & (historical_df['purchase_date'] <= prediction_date)]
            product_features[prod] = {
                'product_total_sales': prod_hist['quantity'].sum(),
                'product_avg_price': prod_hist['price'].mean(),
                'product_surplus_ratio': prod_hist['surplus_flag'].mean()
            }
        for prod in customer_products:
            cp_hist = historical_df[(historical_df['customer_id'] == customer_id) &
                                    (historical_df['product_id'] == prod) &
                                    (historical_df['purchase_date'] <= prediction_date)]
            if cp_hist.empty:
                continue
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
            }
            features.update(customer_features)
            features.update(product_features[prod])
            candidate_features.append(features)
        return pd.DataFrame(candidate_features)

    def compute_recommendation_score(self, prob_7d, prob_14d, qty_7d, qty_14d, surplus_ratio):
        weighted_prob = 0.6 * prob_7d + 0.4 * prob_14d
        avg_qty = (qty_7d + qty_14d) / 2
        surplus_bonus = 1 + surplus_ratio
        score = weighted_prob * avg_qty * surplus_bonus
        return score

    def recommend_for_customer(self, historical_df, customer_id, prediction_date, top_n=10):
        candidates = self.generate_candidate_products(historical_df, customer_id, prediction_date)
        if candidates.empty:
            return pd.DataFrame()
        prob_7d, qty_7d = self.models.predict(candidates, 7)
        prob_14d, qty_14d = self.models.predict(candidates, 14)
        scores = []
        for i in range(len(candidates)):
            score = self.compute_recommendation_score(
                prob_7d[i], prob_14d[i], qty_7d[i], qty_14d[i], candidates.iloc[i]['product_surplus_ratio']
            )
            scores.append(score)
        candidates['score'] = scores
        candidates['prob_7d'] = prob_7d
        candidates['prob_14d'] = prob_14d
        candidates['qty_7d'] = qty_7d
        candidates['qty_14d'] = qty_14d
        recommendations = candidates.sort_values('score', ascending=False).head(top_n)
        return recommendations[['customer_id', 'product_id', 'score', 'prob_7d', 'prob_14d', 'qty_7d', 'qty_14d']]