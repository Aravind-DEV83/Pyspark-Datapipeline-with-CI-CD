# 🚀 Scalable PySpark Data Pipeline on GCP

This project demonstrates an end-to-end scalable data pipeline built with PySpark on GCP, featuring fully automated CI/CD GitHub actions workflows and job orchestration with Airflow for seamless deployment and testing across staging and production environments

# Solution Architecture

![alt text](files/final-ci:cd.png)

Integrated Apache Airflow with GitHub Actions to orchestrate and automate PySpark batch jobs on Google Cloud Platform.

* Trigger a GitHub Actions workflow on PR creation against the develop branch to:

    * Authenticate and set up access to GCP.
    * Upload test data and PySpark scripts to a GCS bucket.

* On merging to the develop branch:

    * GitHub Actions initiates an Airflow DAG that runs both unit and integration tests.
    * On successful validation, the DAG submits the PySpark job to the staging Dataproc cluster.

* After merging to the master branch: GitHub workflow triggers a production Airflow DAG that:

    * Validates code via unit/integration tests.
    * Submits the PySpark job to the production Dataproc cluster.

## Security & Access Control

### Service Accounts

| Service Account           | Permisssions                   |
| ------------------------- |:-------------------------------|
| wkf-oidc                  | Workload Identity User         |
|                           | Service Account Token Creator  | 
|                           | Dataproc Editor                |
|                           | BigQuery Job User              |
|                           | BigQuery Data Editor           |
|                           | Storage Object Admin           |
|                           |
| composer-service-account  | BigQuery Admin                 |
|                           | Composer Administrator         |
|                           | Composer Worker                |
|                           | Dataproc Editor                |
|                           | Storage Admin                  |
|                           | Service Account User           |


### Google Cloud & GitHub Keyless Authentication

The GitHub action authenticates to google cloud via the `Workload Identity Federation` is recomended over the service account keys that needs to exported to GitHub secrets which is long-lived. 

With GitHub's introudction of OIDC tokens into GitHub action workflows, that enables the user to authenticate from GitHub actions to Google Cloud using `Workload Identity Federation`, by removing the need to long-lived service account key.

[Workload Identity Federation through a Service Account](https://github.com/google-github-actions/auth?tab=readme-ov-file#workload-identity-federation-through-a-service-account)


### 1. Create a Workload Identity Pool:

```
gcloud iam workload-identity-pools create "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"
``` 
### 2. Get the full ID of the Workload Identity Pool:

```
gcloud iam workload-identity-pools describe "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)"
```
This value should be of the format: *projects/123456789/locations/global/workloadIdentityPools/github*
