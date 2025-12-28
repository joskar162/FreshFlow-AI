import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, mean_absolute_error
import joblib

class HarvestIQModels:
    def __init__(self):
        self.classifier_7d = RandomForestClassifier(n_estimators=100, random_state=42)
        self.classifier_14d = RandomForestClassifier(n_estimators=100, random_state=42)
        self.regressor = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_features(self, df):
        """
        Prepare features for modeling by dropping non-feature columns.

        Parameters:
        - df: DataFrame with features and labels

        Returns:
        - X, y_class, y_reg: Feature matrix and targets
        """
        # Drop label columns and identifiers
        drop_cols = ['customer_id', 'product_id', 'cp_last_purchase_date', 'last_purchase_date',
                     'future_quantity', 'future_purchases', 'will_buy', 'window']
        X = df.drop(columns=drop_cols, errors='ignore')

        # For classification
        y_class = df['will_buy']

        # For regression (only on positive samples)
        y_reg = df[df['will_buy'] == 1]['future_quantity']

        return X, y_class, y_reg

    def train_classifiers(self, data_7d, data_14d):
        """
        Train classification models for 7d and 14d windows.

        Parameters:
        - data_7d: Preprocessed data for 7-day window
        - data_14d: Preprocessed data for 14-day window
        """
        # 7-day model
        X_7d, y_7d, _ = self.prepare_features(data_7d)
        X_train_7d, X_test_7d, y_train_7d, y_test_7d = train_test_split(X_7d, y_7d, test_size=0.2, random_state=42)
        self.classifier_7d.fit(X_train_7d, y_train_7d)

        # Evaluate
        y_pred_proba_7d = self.classifier_7d.predict_proba(X_test_7d)[:, 1]
        auc_7d = roc_auc_score(y_test_7d, y_pred_proba_7d)
        print(f"7-day Classifier AUC: {auc_7d:.4f}")

        # 14-day model
        X_14d, y_14d, _ = self.prepare_features(data_14d)
        X_train_14d, X_test_14d, y_train_14d, y_test_14d = train_test_split(X_14d, y_14d, test_size=0.2, random_state=42)
        self.classifier_14d.fit(X_train_14d, y_train_14d)

        y_pred_proba_14d = self.classifier_14d.predict_proba(X_test_14d)[:, 1]
        auc_14d = roc_auc_score(y_test_14d, y_pred_proba_14d)
        print(f"14-day Classifier AUC: {auc_14d:.4f}")

    def train_regressor(self, data_7d, data_14d):
        """
        Train regression model for quantity prediction.

        Parameters:
        - data_7d: Preprocessed data for 7-day window
        - data_14d: Preprocessed data for 14-day window
        """
        # Combine positive samples from both windows
        pos_7d = data_7d[data_7d['will_buy'] == 1]
        pos_14d = data_14d[data_14d['will_buy'] == 1]
        pos_data = pd.concat([pos_7d, pos_14d])

        X_reg, _, y_reg = self.prepare_features(pos_data)
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
        self.regressor.fit(X_train_reg, y_train_reg)

        # Evaluate
        y_pred_reg = self.regressor.predict(X_test_reg)
        mae = mean_absolute_error(y_test_reg, y_pred_reg)
        print(f"Regressor MAE: {mae:.4f}")

    def predict(self, features_df, window):
        """
        Make predictions for given features.

        Parameters:
        - features_df: DataFrame with features
        - window: 7 or 14

        Returns:
        - prob: Purchase probability
        - qty: Predicted quantity (if prob > 0)
        """
        X = features_df.drop(columns=['customer_id', 'product_id', 'cp_last_purchase_date', 'last_purchase_date'], errors='ignore')

        if window == 7:
            prob = self.classifier_7d.predict_proba(X)[:, 1]
        elif window == 14:
            prob = self.classifier_14d.predict_proba(X)[:, 1]
        else:
            raise ValueError("Window must be 7 or 14")

        # Predict quantity only if prob > 0.5 or something, but for ranking, predict for all
        qty = self.regressor.predict(X)

        return prob, qty

    def save_models(self, path='harvestiq/models/'):
        """
        Save trained models.

        Parameters:
        - path: Directory to save models
        """
        import os
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.classifier_7d, f'{path}classifier_7d.pkl')
        joblib.dump(self.classifier_14d, f'{path}classifier_14d.pkl')
        joblib.dump(self.regressor, f'{path}regressor.pkl')

    def load_models(self, path='harvestiq/models/'):
        """
        Load trained models.

        Parameters:
        - path: Directory to load models from
        """
        self.classifier_7d = joblib.load(f'{path}classifier_7d.pkl')
        self.classifier_14d = joblib.load(f'{path}classifier_14d.pkl')
        self.regressor = joblib.load(f'{path}regressor.pkl')

if __name__ == "__main__":
    # Example training (would need preprocessed data)
    print("Models module loaded. Use HarvestIQModels class to train and predict.")