import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score, confusion_matrix

# 1. Define Paths
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
    # 2. Load Data and recreate the exact same split
    df = load_data()
    X = df.drop(columns=['Attrition'])
    y = df['Attrition']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 3. Load the PRE-FITTED preprocessing pipeline
    print("Loading preprocessing pipeline...")
    preprocessor = joblib.load(PIPELINE_PATH)
    
    # Transform the data
    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # 4. Train Logistic Regression with Class Weights (to handle imbalance)
    print("Training Logistic Regression baseline...")
    model = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
    model.fit(X_train_processed, y_train)
    
    # 5. Evaluate on the test set
    y_pred = model.predict(X_test_processed)
    y_proba = model.predict_proba(X_test_processed)[:, 1]
    
    print("\n--- Confusion Matrix ---")
    print(confusion_matrix(y_test, y_pred))
    
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=['Stayed (0)', 'Left (1)']))
    
    print("\n--- Advanced Metrics ---")
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")
    print(f"Average Precision (AP): {average_precision_score(y_test, y_proba):.4f}")