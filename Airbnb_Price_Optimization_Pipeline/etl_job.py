import boto3
import pandas as pd
from io import BytesIO, StringIO

s3 = boto3.client('s3')
bucket = 'raw-data-sc171'
input_key = 'airbnb_ratings_new.csv'
output_key = 'processed/airbnb_ratings_new.csv'

response = s3.get_object(Bucket=bucket, Key=input_key)
raw_bytes = response['Body'].read()


df = pd.read_csv(BytesIO(raw_bytes),
                 encoding='latin1',
                 sep=',',
                 na_values=['', 'NA', 'NaN', 'null'],
                 low_memory=False)


df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')


def clean_airbnb_data(df):
    df = df.dropna(axis=1, how='all')         
    df = df.drop_duplicates()                  
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')

    score_cols = [col for col in df.columns if 'review_scores' in col]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())

    if 'price' in df.columns:
        def price_tier(p):
            if pd.isna(p): return 'Unknown'
            elif p < 50: return 'Budget'
            elif p < 150: return 'Mid-range'
            elif p < 300: return 'Upper Mid-range'
            else: return 'Luxury'
        df['price_tier'] = df['price'].apply(price_tier)

    return df

df_clean = clean_airbnb_data(df)


buffer = StringIO()
df_clean.to_csv(buffer, index=False)
s3.put_object(Bucket=bucket, Key=output_key, Body=buffer.getvalue())