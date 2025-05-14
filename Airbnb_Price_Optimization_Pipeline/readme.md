# Airbnb Price Optimization Pipeline (AWS Serverless)

This repository contains a fully serverless data and machine learning pipeline built on AWS to help Airbnb property owners determine fair rental pricing and gain insights into customer satisfaction metrics and price-tier performance. 

Sources from: https://www.kaggle.com/datasets/samyukthamurali/airbnb-ratings-dataset

---

## 🧠 Project Objective

To automate the ingestion, processing, and analysis of Airbnb listing data, and to deploy a machine learning model (K-Nearest Neighbors) that predicts nightly rental prices based on listing attributes such as property type, room type, location, and amenities. The pipeline also generates analytical insights on customer review scores and performance across price tiers.

<img width="500" alt="Screenshot 2025-05-13 at 5 35 57 PM" src="https://github.com/user-attachments/assets/7b01b380-8ac2-4ef5-8f9a-04f421a7675f" />
<img width="940" alt="Screenshot 2025-05-13 at 5 36 22 PM" src="https://github.com/user-attachments/assets/81ae6801-b315-4c41-a230-42cc83102ebe" />


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

  ![Screenshot 2025-05-13 at 12 34 26 PM](https://github.com/user-attachments/assets/8023f32b-f645-40fc-afef-78710a961060)


### 🔹 Review Score Insights
- Aggregates customer satisfaction scores by property type.
- Stores results in `property_insights.csv` and pushes to RDS.


### 🔹 Price Tier Analytics
- Segments listings into tiers (e.g., <$50, $50–149, $150–299).
- Analyzes perceived value and accuracy per segment.
- Output stored in `price_range.csv` for dashboarding or querying.

![Screenshot 2025-05-12 at 9 04 53 PM](https://github.com/user-attachments/assets/fd7c20fe-e2d5-44c2-af4d-2cfbf400c719)


---

## 🔐 Security & IAM Best Practices

- IAM roles are scoped with least privilege per Lambda/Glue/SageMaker job.
- RDS access is limited to secure VPCs and controlled security groups.
- S3 enforces server-side encryption and HTTPS-only bucket policies.
- SNS topics and ALB health checks ensure observability and reliability.

---

## 🚀 Deployment

### How to Use This AWS Data Engineering Pipeline Project

This guide outlines the steps to set up, deploy, and run the data engineering pipeline demonstrated in this repository. This project is designed to showcase a data pipeline on AWS, primarily using Python and Shell scripts.

### Table of Contents

1.  [Prerequisites](#prerequisites)
2.  [Setup Instructions](#setup-instructions)
    *   [Clone the Repository](#clone-the-repository)
    *   [Configure AWS Credentials](#configure-aws-credentials)
    *   [Install Dependencies](#install-dependencies)
    *   [Configure Pipeline Parameters](#configure-pipeline-parameters)
3.  [Deploying the Pipeline](#deploying-the-pipeline)
4.  [Running the Pipeline](#running-the-pipeline)
5.  [Monitoring the Pipeline](#monitoring-the-pipeline)
6.  [Cleaning Up Resources](#cleaning-up-resources)
7.  [Troubleshooting](#troubleshooting)

---

### 1. Prerequisites

Before you begin, ensure you have the following:

*   **AWS Account**: An active AWS account with appropriate permissions to create and manage necessary resources (e.g., S3, Lambda, Glue, Step Functions, IAM roles).
*   **AWS CLI**: The AWS Command Line Interface installed and configured on your local machine. You can configure it by running `aws configure`.
    *   [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
    *   [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
*   **Python**: Python 3.8 or higher installed on your local machine.
    *   [Install Python](https://www.python.org/downloads/)
*   **Git**: Git installed on your local machine to clone the repository.
    *   [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
*   **(Optional) AWS CDK or CloudFormation Knowledge**: If the project uses Infrastructure as Code (IaC) tools like AWS CDK or CloudFormation, familiarity with them will be helpful.
*   **(Optional) Docker**: If any part of the pipeline uses Docker containers.

---

### 2. Setup Instructions

#### Clone the Repository

1.  Open your terminal or command prompt.
2.  Clone the repository to your local machine:
    ```bash
    git clone https://github.com/jimmy-chen-1/AWS_Pipeline_Project.git
    cd AWS_Pipeline_Project
    ```

#### Configure AWS Credentials

Ensure your AWS CLI is configured with credentials that have sufficient permissions to deploy and manage the pipeline resources. Typically, this involves setting your `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`.

You can verify your current configuration by running:
```bash
aws sts get-caller-identity
```

#### Install Dependencies

This project primarily uses Python and Shell. Python dependencies are usually managed with a `requirements.txt` file.

1.  **(Optional)** Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` doesn't exist, check the project for specific Python package installation instructions or scripts.)*

Shell scripts (`.sh`) might have their own dependencies (like `jq`, `awscli` already covered). Ensure these are available in your PATH.

#### Configure Pipeline Parameters

Data pipelines often require configuration for things like S3 bucket names, database connection strings, API endpoints, or environment settings (dev, prod).

*   Look for configuration files (e.g., `config.json`, `config.yaml`, `.env`, or scripts like `setup_env.sh`).
*   Update these files with your specific AWS resource names, ARNs, or other parameters as required by the pipeline.
*   **Example**: You might need to specify an S3 bucket for data input/output or a specific IAM role ARN.

---

### 3. Deploying the Pipeline

Deployment might involve running scripts that use AWS SDK (like Boto3 in Python) or IaC tools.

*   **Using Shell Scripts**:
    Look for deployment scripts (e.g., `deploy.sh`, `setup_pipeline.sh`).
    ```bash
    chmod +x deploy.sh  # Make the script executable
    ./deploy.sh
    ```
*   **Using Python Scripts**:
    Look for Python deployment scripts (e.g., `deploy.py`, `setup_infra.py`).
    ```bash
    python deploy.py
    ```
*   **Using AWS CDK/CloudFormation**:
    If the project uses CDK:
    ```bash
    cdk bootstrap # If first time using CDK in the region/account
    cdk deploy
    ```
    If the project uses CloudFormation directly, you might use the AWS CLI:
    ```bash
    aws cloudformation deploy --template-file template.yaml --stack-name MyDataPipelineStack --capabilities CAPABILITY_IAM
    ```

Check the project's documentation or scripts for the exact deployment command. The deployment process will create the necessary AWS resources (e.g., S3 buckets, Lambda functions, Glue jobs, Step Functions state machines, IAM roles).

---

### 4. Running the Pipeline

Once deployed, the pipeline can be triggered in several ways:

*   **Manual Trigger**:
    *   Via AWS Console: Navigate to the primary service orchestrating the pipeline (e.g., AWS Step Functions, AWS Lambda, AWS Glue) and manually start an execution.
    *   Via AWS CLI:
        ```bash
        aws stepfunctions start-execution --state-machine-arn <your-state-machine-arn> --input "{}"
        # or for Lambda:
        # aws lambda invoke --function-name <your-function-name> response.json
        ```
*   **Scheduled Trigger**:
    If the pipeline is designed to run on a schedule (e.g., using Amazon EventBridge Scheduler or a cron-like setup), it should run automatically. You might need to enable or configure the schedule as part of the deployment or a post-deployment step.
*   **Event-Based Trigger**:
    If the pipeline is triggered by an event (e.g., a new file landing in an S3 bucket), ensure the event source and trigger are correctly configured (often done during deployment). To test, you would perform the action that generates the event (e.g., upload a file to the designated S3 bucket).

Refer to the project's specific scripts or documentation (e.g., `run_pipeline.sh` or `trigger.py`) for instructions on how to start it.

---

### 5. Monitoring the Pipeline

You can monitor the pipeline's execution and logs through various AWS services:

*   **Amazon CloudWatch Logs**: Most AWS services, including Lambda, Glue, and Step Functions, send logs to CloudWatch. Check the relevant Log Groups for execution details and errors.
*   **AWS Step Functions Console**: If Step Functions is used, its console provides a visual workflow of executions, showing the status of each step.
*   **AWS Glue Console**: For Glue jobs, the console shows job run history, status, and logs.
*   **Amazon S3**: Check input and output S3 buckets for data movement and processing results.
*   **CloudWatch Alarms/Dashboards**: If configured, these can provide a higher-level view of pipeline health and performance.

---

### 6. Cleaning Up Resources

To avoid ongoing AWS charges, it's important to delete the resources created by the pipeline when they are no longer needed.

*   Look for cleanup scripts (e.g., `cleanup.sh`, `teardown.py`, `destroy.sh`).
    ```bash
    ./cleanup.sh
    # or
    # python teardown.py
    ```
*   **Using AWS CDK/CloudFormation**:
    If deployed with CDK:
    ```bash
    cdk destroy
    ```
    If deployed with CloudFormation:
    ```bash
    aws cloudformation delete-stack --stack-name MyDataPipelineStack
    ```
*   **Manual Deletion**: If no automated cleanup script is provided, you will need to manually delete the resources via the AWS Management Console or AWS CLI. Be careful to delete resources in the correct order to avoid dependency issues (e.g., delete Lambda functions before IAM roles they use, if the roles are specific to them).

---

### 7. Troubleshooting

*   **Permissions Issues (IAM)**: Many errors are due to insufficient IAM permissions. Check CloudWatch logs for "AccessDenied" errors and ensure the IAM roles used by your pipeline services have the necessary policies attached.
*   **Configuration Errors**: Double-check your configuration files for typos, incorrect resource names, or region mismatches.
*   **Dependency Issues**: Ensure all Python packages are installed correctly and that any system-level dependencies for Shell scripts are met.
*   **AWS Service Limits**: For large-scale pipelines, you might hit AWS service limits. Check the limits and request increases if necessary.
*   **Check CloudWatch Logs**: This is often the first place to look for detailed error messages.

---

This guide provides a general overview. Refer to specific scripts and any documentation within the `jimmy-chen-1/AWS_Pipeline_Project` repository for more precise instructions.

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
Website: [@jimmychen-ai](https://jimmyai.uk)  
LinkedIn: [linkedin.com/in/shengjie-chen](https://www.linkedin.com/in/chen-shengjie)


