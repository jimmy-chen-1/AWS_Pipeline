# Airbnb Price Optimization Pipeline (AWS Serverless)

This repository contains a fully serverless data and machine learning pipeline built on AWS to help Airbnb property owners determine fair rental pricing and gain insights into customer satisfaction metrics and price-tier performance.

---

## 🧠 Project Objective

To automate the ingestion, processing, and analysis of Airbnb listing data, and to deploy a machine learning model (K-Nearest Neighbors) that predicts nightly rental prices based on listing attributes such as property type, room type, location, and amenities. The pipeline also generates analytical insights on customer review scores and performance across price tiers.

---

## 🗂️ Files and Folders

- `ml_data.csv` – Cleaned dataset used for ML model training.
- `ml_model.pkl` – Serialized KNN model used in EC2 inference.
- `property_insights.csv` – Aggregated review scores by property type.
- `price_range.csv` – Analysis of value/accuracy across price bands.
- `lambda/` – Folder containing Lambda function code.
- `glue/` – Glue ETL scripts and schema definitions.
- `step_functions/` – ASL definitions for Step Functions orchestration.
- `docs/architecture_diagram.png` – Visual overview of the pipeline.
- `README.md` – Project documentation (this file).

---

## ⚙️ AWS Architecture Overview

This project uses the following AWS services:

| Service            | Purpose |
|--------------------|---------|
| **Amazon S3**      | Stores raw and processed CSV files, model artifacts. |
| **AWS Glue**       | Automates schema inference and ETL transformations. |
| **Amazon RDS (MySQL)** | Stores query results and transformed tabular data. |
| **AWS Lambda**     | Orchestrates logic, processing, and API automation. |
| **Amazon SageMaker** | Trains KNN model for price prediction. |
| **EC2 + Auto Scaling** | Hosts the ML inference web service. |
| **Application Load Balancer (ALB)** | Routes public traffic to EC2 model API. |
| **AWS Step Functions** | Coordinates ETL, ML, and analytics workflows. |
| **Amazon SNS**     | Sends real-time success/failure notifications. |

---

## 📊 Functional Features

### 🔹 Price Prediction
- Trains a KNN model on `ml_data.csv`.
- Predicts nightly prices via a Flask app hosted on EC2.
- Accessible through a web form behind ALB.

### 🔹 Review Score Insights
- Aggregates customer satisfaction scores by property type.
- Stores results in `property_insights.csv` and pushes to RDS.

### 🔹 Price Tier Analytics
- Segments listings into tiers (e.g., <$50, $50–149, $150–299).
- Analyzes perceived value and accuracy per segment.
- Output stored in `price_range.csv` for dashboarding or querying.

---

## 🔐 Security & IAM Best Practices

- IAM roles are scoped with least privilege per Lambda/Glue/SageMaker job.
- RDS access is limited to secure VPCs and controlled security groups.
- S3 enforces server-side encryption and HTTPS-only bucket policies.
- SNS topics and ALB health checks ensure observability and reliability.

---

## 🚀 Deployment

1. Upload raw dataset to S3: `s3://raw-data-sc171/airbnb_ratings_new.csv`
2. Trigger the Step Function `AirbnbMasterPipeline`.
3. Monitor status in Step Functions and SNS.
4. Access the EC2-hosted web UI via ALB DNS to use the prediction model.

---

## 📝 Results Summary

- **Model performance**: KNN RMSE ≈ **97.68**
- **Key insight 1**: Upper mid-range listings ($150–$299) have the highest accuracy and value scores despite lowest volume.
- **Key insight 2**: Villas and guest suites offer best review scores, ideal for premium promotion.
- **Key insight 3**: Dorms, boats, and RVs underperform in value, signaling service redesign needs.

---

## 📄 License

MIT License. See `LICENSE` file for details.

---

## 👤 Author

Shengjie (Jimmy) Chen  
MS Business Analytics @ UIUC  
GitHub: [@jimmychen-ai](https://jimmyai.uk)  
LinkedIn: [linkedin.com/in/shengjie-chen](https://linkedin.com/in/shengjie-chen)


