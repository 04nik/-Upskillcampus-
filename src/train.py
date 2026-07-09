import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import pickle

# Import features functions
from features import generate_features

# Safe import of XGBoost
try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("XGBoost not available. Falling back to RandomForest/GradientBoosting.")

def train_and_evaluate():
    print("Loading data for training...")
    train_raw = pd.read_csv(os.path.join("data", "train.csv"))
    test_raw = pd.read_csv(os.path.join("data", "test.csv"))
    
    # Process features
    train_df, test_df = generate_features(train_raw, test_raw)
    
    # Feature columns for modeling (Junction is handled by training a model per junction)
    features = [
        'Hour', 'DayOfWeek', 'Day', 'Month', 'Year', 'DayOfYear', 
        'IsWeekend', 'IsHoliday', 'jh_mean', 'jdow_mean', 'jhdow_mean', 'jhhol_mean'
    ]
    target = 'Vehicles'
    
    # Time-based validation split (last 2 months: May and June 2017)
    train_df['DateTime'] = pd.to_datetime(train_df['DateTime'])
    test_df['DateTime'] = pd.to_datetime(test_df['DateTime'])
    
    split_date = pd.to_datetime("2017-05-01 00:00:00")
    val_mask = train_df['DateTime'] >= split_date
    
    train_part = train_df[~val_mask]
    val_part = train_df[val_mask]
    
    print(f"Training split: {train_part.shape[0]} rows (Before May 2017)")
    print(f"Validation split: {val_part.shape[0]} rows (May 2017 - June 2017)")
    
    junctions = sorted(train_df['Junction'].unique())
    
    # We will evaluate two algorithms: Random Forest and XGBoost (if available, else Gradient Boosting)
    models_to_test = {
        'RandomForest': lambda: RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    }
    if XGB_AVAILABLE:
        models_to_test['XGBoost'] = lambda: XGBRegressor(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42, n_jobs=-1)
    else:
        models_to_test['GradientBoosting'] = lambda: GradientBoostingRegressor(n_estimators=100, random_state=42)
        
    validation_results = {}
    
    print("\n--- Model Evaluation on Validation Set ---")
    for model_name, model_fn in models_to_test.items():
        print(f"\nEvaluating {model_name}...")
        metrics_per_junction = {}
        
        all_val_preds = []
        all_val_targets = []
        
        for j in junctions:
            # Filter data for this junction
            tr_j = train_part[train_part['Junction'] == j]
            val_j = val_part[val_part['Junction'] == j]
            
            X_tr, y_tr = tr_j[features], tr_j[target]
            X_val, y_val = val_j[features], val_j[target]
            
            # Train model
            model = model_fn()
            model.fit(X_tr, y_tr)
            
            # Predict
            preds = model.predict(X_val)
            # Clip predictions to 0 since vehicles count cannot be negative
            preds = np.clip(preds, 0, None)
            
            # Evaluate
            mae = mean_absolute_error(y_val, preds)
            rmse = root_mean_squared_error(y_val, preds)
            r2 = r2_score(y_val, preds)
            
            metrics_per_junction[j] = {'MAE': mae, 'RMSE': rmse, 'R2': r2}
            print(f"  Junction {j} -> MAE: {mae:.2f} | RMSE: {rmse:.2f} | R2: {r2:.4f}")
            
            all_val_preds.extend(preds)
            all_val_targets.extend(y_val)
            
        overall_mae = mean_absolute_error(all_val_targets, all_val_preds)
        overall_rmse = root_mean_squared_error(all_val_targets, all_val_preds)
        overall_r2 = r2_score(all_val_targets, all_val_preds)
        
        print(f"  OVERALL -> MAE: {overall_mae:.2f} | RMSE: {overall_rmse:.2f} | R2: {overall_r2:.4f}")
        validation_results[model_name] = {
            'overall_mae': overall_mae,
            'overall_rmse': overall_rmse,
            'overall_r2': overall_r2,
            'junction_metrics': metrics_per_junction
        }
        
    # Choose best model based on overall RMSE
    best_algo = min(validation_results.keys(), key=lambda k: validation_results[k]['overall_rmse'])
    print(f"\n>>> Selected Best Model: {best_algo} <<<")
    
    # Train final models on FULL training data and generate test forecast
    print("\nTraining final models on full training data...")
    final_models = {}
    test_preds = np.zeros(test_df.shape[0])
    
    # Store validation predictions for dashboard viz
    val_preds_df = val_part[['ID', 'DateTime', 'Junction', 'Vehicles']].copy()
    val_preds_df['Predicted_Vehicles'] = 0.0
    
    for j in junctions:
        # Full training data for this junction
        full_tr_j = train_df[train_df['Junction'] == j]
        X_full = full_tr_j[features]
        y_full = full_tr_j[target]
        
        # Train
        model = models_to_test[best_algo]()
        model.fit(X_full, y_full)
        final_models[j] = model
        
        # Predict on validation partition for validation plotting
        val_mask_j = (val_preds_df['Junction'] == j)
        X_val_j = val_part[val_part['Junction'] == j][features]
        val_preds_df.loc[val_mask_j, 'Predicted_Vehicles'] = np.clip(model.predict(X_val_j), 0, None)
        
        # Predict on Test data
        test_mask_j = (test_df['Junction'] == j)
        X_test_j = test_df[test_mask_j][features]
        test_preds[test_mask_j] = np.clip(model.predict(X_test_j), 0, None)
        
    # Save the predictions to test_df
    test_df['Vehicles'] = test_preds.astype(int)
    
    # Save forecasts in different formats
    os.makedirs("data", exist_ok=True)
    
    # 1. Standard submission format (ID, Vehicles)
    submission = test_df[['ID', 'Vehicles']]
    submission.to_csv(os.path.join("data", "submission.csv"), index=False)
    print("Saved submission file to data/submission.csv")
    
    # 2. Detailed forecast results (for dashboard charting)
    detailed_forecast = test_df[['ID', 'DateTime', 'Junction', 'Vehicles']].copy()
    detailed_forecast.to_csv(os.path.join("data", "forecast_results.csv"), index=False)
    print("Saved detailed forecast results to data/forecast_results.csv")
    
    # Save validation predictions for dashboard
    val_preds_df.to_csv(os.path.join("data", "val_predictions.csv"), index=False)
    
    # Save model performance stats for dashboard use
    stats_df = pd.DataFrame([
        {
            'Junction': j,
            'MAE': validation_results[best_algo]['junction_metrics'][j]['MAE'],
            'RMSE': validation_results[best_algo]['junction_metrics'][j]['RMSE'],
            'R2': validation_results[best_algo]['junction_metrics'][j]['R2'],
            'Model_Type': best_algo
        } for j in junctions
    ])
    stats_df.to_csv(os.path.join("data", "model_performance.csv"), index=False)
    print("Saved model performance statistics to data/model_performance.csv")
    
    print("\nTraining and Forecasting Completed Successfully!")

if __name__ == "__main__":
    train_and_evaluate()
