import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# 1. Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, "ml", "data", "raw", "WA_Fn-UseC_-HR-Employee-Attrition.csv")
MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")
PIPELINE_PATH = os.path.join(MODEL_DIR, "preprocessing_pipeline.joblib")

def load_and_clean_data():
    print("Loading raw data...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Drop columns that are constant or pure identifiers (Leakage Audit)
    # EmployeeCount, Over18, StandardHours have only 1 unique value. EmployeeNumber is an ID.
    cols_to_drop = ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber']
    df = df.drop(columns=cols_to_drop)
    
    # Drop any rows where the target is missing (handles weird blank lines in CSV)
    df = df.dropna(subset=['Attrition'])
    
    # Force the target to be a numeric type, then convert to integer
    df['Attrition'] = pd.to_numeric(df['Attrition'], errors='coerce')
    
    # Drop any rows that failed the numeric conversion
    df = df.dropna(subset=['Attrition'])
    df['Attrition'] = df['Attrition'].astype(int)
    
    return df

def build_pipeline(X_train):
    # Identify numeric and categorical columns
    numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X_train.select_dtypes(include=['str', 'object']).columns.tolist()
    
    # Numeric pipeline: Impute missing values (if any) and scale
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Categorical pipeline: Impute missing values and One-Hot Encode
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # Combine into a ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    return preprocessor

if __name__ == "__main__":
    # 1. Load Data
    df = load_and_clean_data()
    
    # 2. Split features (X) and target (y)
    X = df.drop(columns=['Attrition'])
    y = df['Attrition']
    
    # 3. Train/Test Split (Stratified because the dataset is imbalanced)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Build the preprocessor
    preprocessor = build_pipeline(X_train)
    
    # 5. FIT on training data ONLY (prevents data leakage!)
    print("Fitting preprocessing pipeline on training data...")
    preprocessor.fit(X_train)
    
    # 6. Save the fitted pipeline for later use in the Frappe App
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    joblib.dump(preprocessor, PIPELINE_PATH)
    
    print(f"Pipeline saved successfully to {PIPELINE_PATH}")
    
    # Quick sanity check
    X_train_processed = preprocessor.transform(X_train)
    print(f"Original training shape: {X_train.shape}")
    print(f"Processed training shape: {X_train_processed.shape}")