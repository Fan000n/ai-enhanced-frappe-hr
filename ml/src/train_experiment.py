import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
import time

# 1. Define Paths and Load Data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, "ml", "data", "raw", "WA_Fn-UseC_-HR-Employee-Attrition.csv")
PIPELINE_PATH = os.path.join(BASE_DIR, "ml", "models", "preprocessing_pipeline.joblib")

def load_data():
    df = pd.read_csv(RAW_DATA_PATH)
    df = df.dropna(subset=['Attrition'])
    df['Attrition'] = pd.to_numeric(df['Attrition'], errors='coerce').dropna().astype(int)
    df = df.drop(columns=['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber'])
    return df

if __name__ == "__main__":
    df = load_data()
    X = df.drop(columns=['Attrition'])
    y = df['Attrition']
    
    # Split into Train and Test (Test remains untouched!)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    preprocessor = joblib.load(PIPELINE_PATH)
    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Define the models and their hyperparameter grids to search
    models = {
        "Logistic Regression": {
            "model": LogisticRegression(class_weight='balanced', random_state=42, max_iter=2000),
            "params": {"C": [0.01, 0.1, 1, 10]}
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(class_weight='balanced', random_state=42),
            "params": {"max_depth": [3, 5, 10, None], "min_samples_split": [2, 10, 20]}
        },
        "Random Forest": {
            "model": RandomForestClassifier(class_weight='balanced', random_state=42),
            "params": {"n_estimators": [100, 200], "max_depth": [5, 10, None]}
        }
    }
    
    results = []
    
    print("Starting Model Experimentation and Tuning...\n")
    
    for name, config in models.items():
        print(f"--- Tuning {name} ---")
        start_time = time.time()
        
        # GridSearchCV evaluates based on Average Precision (AP) because it's best for imbalance
        grid_search = GridSearchCV(
            estimator=config["model"],
            param_grid=config["params"],
            scoring='average_precision',
            cv=5, # 5-fold cross-validation
            n_jobs=-1 # Use all CPU cores
        )
        
        grid_search.fit(X_train_processed, y_train)
        best_model = grid_search.best_estimator_
        
        # Evaluate on the test set just to report, but we will lock the model later
        y_proba = best_model.predict_proba(X_test_processed)[:, 1]
        test_ap = average_precision_score(y_test, y_proba)
        test_roc = roc_auc_score(y_test, y_proba)
        
        elapsed = time.time() - start_time
        
        results.append({
            "Model": name,
            "Best Params": grid_search.best_params_,
            "CV AP (Validation)": grid_search.best_score_,
            "Test AP": test_ap,
            "Test ROC-AUC": test_roc,
            "Time (s)": elapsed
        })
        print(f"Finished {name} in {elapsed:.2f}s. Best CV AP: {grid_search.best_score_:.4f}\n")
        
    # Display a clean comparison table
    results_df = pd.DataFrame(results)
    print("\n--- Model Comparison Results ---")
    print(results_df[["Model", "CV AP (Validation)", "Test AP", "Test ROC-AUC"]].round(4).to_string(index=False))