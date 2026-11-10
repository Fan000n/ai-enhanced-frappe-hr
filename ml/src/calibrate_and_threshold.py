import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, precision_score, recall_score, f1_score

# 1. Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, "ml", "data", "raw", "WA_Fn-UseC_-HR-Employee-Attrition.csv")
PIPELINE_PATH = os.path.join(BASE_DIR, "ml", "models", "preprocessing_pipeline.joblib")
FINAL_MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "final_calibrated_model.joblib")
THRESHOLD_PATH = os.path.join(BASE_DIR, "ml", "models", "locked_threshold.txt")

# 2. Business Costs (from docs/cost_matrix_and_roles.md)
COST_FN = 10000  # Missed a leaver
COST_FP = 500    # False alarm

if __name__ == "__main__":
    df = pd.read_csv(RAW_DATA_PATH)
    df = df.dropna(subset=['Attrition'])
    df['Attrition'] = pd.to_numeric(df['Attrition'], errors='coerce').dropna().astype(int)
    df = df.drop(columns=['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber'])
    
    X = df.drop(columns=['Attrition'])
    y = df['Attrition']
    
    # --- SPLIT 1: The Unseen Test Set (20%) ---
    # We DO NOT touch this until the very end.
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # --- SPLIT 2: Train and Validation (from the 80% training data) ---
    # We use this to calibrate and find the threshold.
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
    )
    
    preprocessor = joblib.load(PIPELINE_PATH)
    X_train_proc = preprocessor.transform(X_train)
    X_val_proc = preprocessor.transform(X_val)
    
    # 3. Train Base LR and Calibrate it
    print("Training and Calibrating Logistic Regression...")
    base_lr = LogisticRegression(class_weight='balanced', random_state=42, max_iter=2000)
    
    # We use cv=5 on the training data to learn the calibration curve.
    # Then we will evaluate it on the untouched X_val to find the threshold.
    calibrated_model = CalibratedClassifierCV(base_lr, method='sigmoid', cv=5)
    
    # Fit the calibrated model ONLY on the training data
    calibrated_model.fit(X_train_proc, y_train)
    
    # Evaluate Calibration
    y_val_proba = calibrated_model.predict_proba(X_val_proc)[:, 1]
    brier = brier_score_loss(y_val, y_val_proba)
    print(f"Brier Score on Validation (lower is better): {brier:.4f}")
    
    # 4. Cost-Sensitive Threshold Selection
    print("\n--- Threshold Evaluation (Validation Set) ---")
    print(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'FN':<5} | {'FP':<5} | {'Total Cost':<10}")
    print("-" * 70)
    
    best_threshold = 0.5
    min_cost = float('inf')
    
    for threshold in np.arange(0.10, 0.91, 0.05):
        # Predict based on custom threshold
        y_pred_custom = (y_val_proba >= threshold).astype(int)
        
        # Calculate metrics
        prec = precision_score(y_val, y_pred_custom, zero_division=0)
        rec = recall_score(y_val, y_pred_custom, zero_division=0)
        
        # Calculate confusion matrix elements
        fn = np.sum((y_val == 1) & (y_pred_custom == 0))
        fp = np.sum((y_val == 0) & (y_pred_custom == 1))
        
        # Calculate financial cost
        cost = (fn * COST_FN) + (fp * COST_FP)
        
        print(f"{threshold:<10.2f} | {prec:<10.2f} | {rec:<10.2f} | {fn:<5} | {fp:<5} | ${cost:<10,.0f}")
        
        if cost < min_cost:
            min_cost = cost
            best_threshold = threshold
            
    print("-" * 70)
    print(f"Optimal Threshold selected: {best_threshold:.2f} (Estimated Cost: ${min_cost:,.0f})")
    
    # 5. Retrain on the FULL training set (Train + Validation) for maximum data usage
    print("\nRetraining final model on full training data...")
    X_full_proc = preprocessor.transform(X_train_full)
    final_base_lr = LogisticRegression(class_weight='balanced', random_state=42, max_iter=2000)
    final_calibrated_model = CalibratedClassifierCV(final_base_lr, method='sigmoid', cv=5) # use 5-fold cv on full data
    final_calibrated_model.fit(X_full_proc, y_train_full)
    
    # 6. Lock and Save Artifacts
    joblib.dump(final_calibrated_model, FINAL_MODEL_PATH)
    with open(THRESHOLD_PATH, 'w') as f:
        f.write(str(round(best_threshold, 2)))
        
    print(f"\nSaved final calibrated model to {FINAL_MODEL_PATH}")
    print(f"Locked threshold {best_threshold:.2f} saved to {THRESHOLD_PATH}")