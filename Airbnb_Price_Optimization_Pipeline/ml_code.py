import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error

# ✅ Step 1
print("[Step 1] ⬇️ Loading CSV from mounted input path...")
input_path = "/opt/ml/processing/input/ml_data.csv"
df = pd.read_csv(input_path)
print(f"[✅] Dataset loaded: {df.shape}")

# Step 2
target_col = 'price'
X = df.drop(columns=[target_col])
y = df[target_col]

# Step 3
categorical = X.select_dtypes(include='object').columns.tolist()
numeric = X.select_dtypes(include=[np.number]).columns.tolist()

def compress_rare_categories(series, threshold=0.01):
    freq = series.value_counts(normalize=True)
    rare = freq[freq < threshold].index
    return series.apply(lambda x: 'RARE' if x in rare else x)

for col in categorical:
    X[col] = compress_rare_categories(X[col], threshold=0.01)

# Step 4: Pipeline
numeric_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean'))
])
categorical_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
])
preprocessor = ColumnTransformer([
    ('num', numeric_pipeline, numeric),
    ('cat', categorical_pipeline, categorical)
])
model_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', HistGradientBoostingRegressor(random_state=42))
])

# Step 5: training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model_pipeline.fit(X_train, y_train)

# Step 6: evaluation
y_pred = model_pipeline.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"[📉 RMSE] {rmse:.2f}")

# ✅ Step 7: 保存模型到挂载输出路径（SageMaker 会自动上传到 S3）
output_path = "/opt/ml/processing/output/ml_model.pkl"
joblib.dump(model_pipeline, output_path)
print(f"[✅] 模型已保存至本地: {output_path}")
