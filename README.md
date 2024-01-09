# IAC-Pulumi

Pulumi is an Infrastructure as Code (IaC) tool designed to help manage and provision cloud resources and infrastructure. Pulumi provides a robust set of libraries, integrations with popular CI/CD tools. 
Pulumi allows you to automate the provisioning and management of cloud infrastructure. You can define your infrastructure in code, and Pulumi will create, update, or delete cloud resources to match the desired state, reducing the manual and error-prone tasks involved in setting up and maintaining infrastructure.

# Overview

This project aims to demonstrate the deployment of a multi-cloud architecture using Infrastructure as Code (IAC) principles. It leverages Pulumi, a cloud infrastructure automation tool, to provision and manage resources on both Amazon Web Services (AWS) and Google Cloud Platform (GCP). The architecture includes various components such as a Virtual Private Cloud (VPC), RDS PostgreSQL database, EC2 instances, an Application Load Balancer (ALB), AWS Lambda functions, and many more.

![Image](https://github.com/Manuindukuri/InfrastructureCode-Pulumi/assets/114769115/397891ca-855c-49c3-9294-4b9249259588)

## Configuration
Configuration for the project is managed using environment variables stored in a .env file. This allows flexibility and customization of various parameters such as region, instance types, database settings, and API keys.

## Key Components
### Amazon Web Services (AWS)

**1. Virtual Private Cloud (VPC):** A VPC is created with public and private subnets. This provides network isolation and allows secure communication between resources.

**2. RDS PostgreSQL Database:** An RDS instance running PostgreSQL is deployed. It uses the specified instance class, storage type, and configurations from environment variables.

**3.Auto Scaling Group (ASG) with EC2 Instances:** An Auto Scaling Group is defined to manage EC2 instances. It ensures high availability and automatically scales the number of instances based on demand.

**4. Application Load Balancer (ALB):** The ALB acts as a reverse proxy to distribute incoming traffic among EC2 instances in the ASG.

**5. CloudWatch Alarms:** CloudWatch alarms are set up to monitor the CPU utilization of EC2 instances. Scaling policies are defined to automatically adjust the ASG size based on the alarms.

**6. AWS Lambda Functions:** Lambda functions are used for various purposes, including processing data, automating tasks, and responding to SNS notifications.

**7. Simple Notification Service (SNS) Topic:** An SNS topic is created to enable event-driven communication between AWS resources.

### Google Cloud Platform (GCP)

**1. Cloud Storage (GCS) Bucket:** A GCS bucket is provisioned to store data and objects securely in the Google Cloud environment.

**2. Google Service Account:** A Google Service Account is created to grant permissions to AWS Lambda functions for interacting with GCS.

### Requirements
- Python 3.x
- Pulumi 3.x.x
- .env file 
- AWS Account

### Installation 
https://www.pulumi.com/docs/install
```bash
$ brew install pulumi/tap/pulumi
```
https://www.pulumi.com/docs/languages-sdks/python

### Create Instance
```bash
$ pulumi up --config aws:profile= Your_Admin_IAM_User
```

### Destroy Stack
Once Everything is checked, delete the instance by:
```bash
$ pulumi destroy
```

# Lambda Packages
```
https://github.com/indukuriCloud/test/raw/main/my_deployment_package.zip
```

# Certificate Import
```
aws acm import-certificate --profile <profile_name> --region us-east-1 --certificate fileb://<cretificate_file_in_crt> --private-key fileb://<private_key_in_pem> --certificate-chain fileb://<ca-bundle_file>PrivateKey.pem
```

### Environment variables:
```
AWS_REGION=YOUR_NEAREST_REGION

AWS_AVAILABILITY_ZONES=AVAILABLE_REGION

MY_PUBLIC_SUBNETS=YOUR_CHOICE

MY_PRIVATE_SUBNETS=YOUR_CHOICE

MY_VPC_CIDR_PREFIX=x.x.x.x/xx(ex:10.0.0.1/16)

MY_VPC_NAME=CHOICE_OF_NAME

MY_SUBNET_PUBLIC_NAME=pulumi-public-subnet-

MY_SUBNET_PRIVATE_NAME=pulumi-private-subnet-

MY_PUBLIC_ROUTE_TABLE=publicRouteTable

MY_PRIVATE_ROUTE_TABLE=privateRouteTable

MY_PUBLIC_SUBNET_CONNECT=public-subnet-connect-

MY_PRIVATE_SUBNET_CONNECT=private-subnet-connect-

MY_INTERNET_GATEWAY=pulumi-internetGateway

MY_PUBLIC_ROUTE=publicRoute

MY_PUBLIC_ROUTE_CIDR_DES=0.0.0.0/0

Instance_Type=t2.micro

AMI=ami-id
```

### RDS Instance Variables
```
export ALLOCATED_STORAGE='10'

export STORAGE_TYPE="gp2"

export ENGINE="Postgres"

export ENGINE_VERSION=""

export INSTANCE_CLASS="db.t3.micro"

export NAME=""

export USERNAME=""

export PASSWORD=""

export DB_NAME=""
```

### GCP 
```
GCP_BUCKET_NAME=

GCP_BUCKER_LOCATION=

PROJECT_ID=
```
### AWS Lambda
```
MAILGUN_API_KEY=

MAILGUN_DOMAIN=

MAILGUN_SENDER=

DYNAMODB_TABLE=

LAMBDA_PACKAGES=

```
### License
This project is licensed under the MIT License.
