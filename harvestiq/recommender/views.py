from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_dummy_data, preprocess_data, HarvestIQModels, HarvestIQRecommender
from .serializers import RecommendationSerializer
import pandas as pd
import os

class TrainModelsView(APIView):
    def post(self, request):
        # Generate data if not exists
        data_path = 'harvestiq/data/transactions.csv'
        if not os.path.exists(data_path):
            os.makedirs('harvestiq/data', exist_ok=True)
            df = generate_dummy_data()
            df.to_csv(data_path, index=False)

        # Preprocess
        preprocessed = preprocess_data(data_path)
        data_7d = preprocessed['7d']
        data_14d = preprocessed['14d']

        # Train models
        models = HarvestIQModels()
        models.train_classifiers(data_7d, data_14d)
        models.train_regressor(data_7d, data_14d)
        models.save_models()

        return Response({"message": "Models trained and saved successfully."}, status=status.HTTP_200_OK)

class RecommendView(APIView):
    def get(self, request, customer_id):
        data_path = 'harvestiq/data/transactions.csv'
        if not os.path.exists(data_path):
            return Response({"error": "Data not found. Please train models first."}, status=status.HTTP_404_NOT_FOUND)

        df = pd.read_csv(data_path, parse_dates=['purchase_date'])
        prediction_date = pd.to_datetime('2024-11-01')  # Same as training

        recommender = HarvestIQRecommender()
        recommendations = recommender.recommend_for_customer(df, customer_id, prediction_date, top_n=5)

        if recommendations.empty:
            return Response({"recommendations": []}, status=status.HTTP_200_OK)

        # Prepare response
        recs = []
        for _, row in recommendations.iterrows():
            # Get surplus_flag from data
            surplus_flag = df[df['product_id'] == row['product_id']]['surplus_flag'].iloc[0] if not df[df['product_id'] == row['product_id']].empty else False
            rec = {
                "product_id": row['product_id'],
                "purchase_probability_7d": float(row['prob_7d']),
                "purchase_probability_14d": float(row['prob_14d']),
                "recommended_quantity": float((row['qty_7d'] + row['qty_14d']) / 2),
                "surplus_flag": bool(surplus_flag)
            }
            recs.append(rec)

        return Response({"recommendations": recs}, status=status.HTTP_200_OK)