# HarvestIQ: Predictive Recommender System for Fresh Produce Retail

HarvestIQ is a machine learning-based recommender system designed to predict customer shopping baskets for fresh produce, with a focus on reducing food waste by prioritizing surplus and odd-looking produce.

## Overview

The system predicts:
1. The probability that a customer will purchase a specific fresh-produce item within the next 7 days and 14 days.
2. The quantity the customer is likely to purchase if they buy.
3. Prioritizes surplus produce to minimize waste.

It uses historical transaction data to build features and train models for personalized recommendations.

## Project Structure

```
harvestiq/
├── data/
│   └── transactions.csv          # Dummy dataset
├── models/
│   ├── classifier_7d.pkl         # Trained 7-day classifier
│   ├── classifier_14d.pkl        # Trained 14-day classifier
│   └── regressor.pkl             # Trained quantity regressor
├── src/
│   ├── generate_data.py          # Script to generate dummy data
│   ├── preprocessing.py          # Data preprocessing and feature engineering
│   ├── models.py                 # Model training and prediction classes
│   ├── recommendations.py        # Recommendation logic and scoring
│   └── main.py                   # Main script to run the system
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation and Setup

1. Install dependencies:
   ```bash
   pip install -r harvestiq/requirements.txt
   ```

2. Run the system:
   ```bash
   cd harvestiq
   python src/main.py
   ```

This will generate dummy data, preprocess it, train models, and output recommendations for a sample customer.

## Data Assumptions

The system assumes historical transaction data with the following columns:
- `customer_id`: Unique identifier for customers
- `product_id`: Unique identifier for products
- `product_category`: Category of the product (e.g., Fruits, Vegetables)
- `purchase_date`: Date of purchase
- `quantity`: Quantity purchased
- `price`: Price per unit
- `surplus_flag`: 1 if surplus/odd-looking produce, 0 otherwise
- `month`: Month of purchase for seasonality

## Model Architecture

### 1. Data Preprocessing and Feature Engineering
- **Customer features**: Total purchases, average quantity, number of unique products, recency
- **Product features**: Total sales, average price, surplus ratio
- **Customer-Product interactions**: Total purchases, average quantity, purchase count, recency, average interval, last month
- **Seasonality**: Month of last purchase

### 2. Classification Model (Purchase Likelihood)
- **Algorithm**: Random Forest Classifier
- **Purpose**: Predict probability of purchase in 7-day and 14-day windows
- **Training**: Separate models for 7d and 14d horizons
- **Evaluation Metric**: ROC-AUC

### 3. Regression Model (Quantity Prediction)
- **Algorithm**: Random Forest Regressor
- **Purpose**: Predict purchase quantity for positive purchase cases
- **Training**: Only on samples where purchase occurred
- **Evaluation Metric**: Mean Absolute Error (MAE)

### 4. Recommendation Logic
- **Scoring**: Combines weighted probability, predicted quantity, and surplus bonus
- **Formula**: `score = (0.6 * prob_7d + 0.4 * prob_14d) * avg_quantity * (1 + surplus_ratio)`
- **Ranking**: Sort products by score descending for top-N recommendations

## Evaluation Metrics

- **ROC-AUC**: Measures classification performance for purchase likelihood
- **MAE**: Measures accuracy of quantity predictions

Example model performance (on dummy data):
- 7-day Classifier AUC: ~0.85
- 14-day Classifier AUC: ~0.82
- Regressor MAE: ~0.5 (units)

## How HarvestIQ Reduces Food Waste

1. **Surplus Prioritization**: Products with higher `surplus_flag` receive a bonus in the recommendation score, encouraging purchase of items that might otherwise be discarded.

2. **Predictive Accuracy**: By accurately forecasting demand, the system helps retailers stock appropriate amounts, reducing overstocking of perishable goods.

3. **Personalized Recommendations**: Tailored suggestions increase purchase likelihood of specific items, including surplus produce, leading to higher utilization rates.

4. **Quantity Estimation**: Predicting exact quantities helps in inventory management, minimizing excess stock that leads to waste.

## Example Output

For a sample customer `CUST_0001`, the system might output:

```
Top 5 recommendations for customer CUST_0001:
   customer_id product_id     score   prob_7d  prob_14d   qty_7d   qty_14d
0   CUST_0001   PROD_005    1.234     0.75      0.80      2.1      2.3
1   CUST_0001   PROD_012    1.089     0.68      0.72      2.5      2.7
2   CUST_0001   PROD_003    0.987     0.62      0.65      2.8      3.0
3   CUST_0001   PROD_018    0.876     0.55      0.58      2.2      2.4
4   CUST_0001   PROD_007    0.765     0.48      0.51      2.6      2.8
```

## Assumptions and Limitations

- Assumes sufficient historical data for each customer-product pair
- Models are trained on past behavior; may not capture sudden changes
- Surplus prioritization assumes surplus items are desirable when recommended
- Dummy data is synthetic; real-world performance may vary
- No deep learning used to keep the solution simple and interpretable

## Future Improvements

- Incorporate external factors (weather, promotions)
- Use more advanced models (e.g., neural networks) for better accuracy
- Add real-time updating of models
- Include customer feedback in recommendations

## License

This project is for educational purposes. Feel free to modify and extend.