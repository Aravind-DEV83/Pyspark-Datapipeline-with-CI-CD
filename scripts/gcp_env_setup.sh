#!bin/bash

# Create two dataproc clusters for staging and prodiction.
gcloud dataproc clusters create staging-env-cluster \
    --enable-component-gateway \
    --bucket pyspark-staging-adev-spark \
    --region asia-south1 \
    --no-address \
    --single-node \
    --master-machine-type n2-standard-2 \
    --master-boot-disk-type pd-balanced \
    --master-boot-disk-size 100 \
    --image-version 2.2-debian12 \
    --project adev-spark

gcloud dataproc clusters create prod-env-cluster \
    --enable-component-gateway \
    --bucket pyspark-staging-adev-spark \
    --region asia-south1 \
    --no-address \
    --single-node \
    --master-machine-type n2-standard-4 \
    --master-boot-disk-type pd-balanced \
    --master-boot-disk-size 100 \
    --image-version 2.2-debian12 \
    --project adev-spark

#Trigger DAG
gcloud composer environments run "${{ env.ENV_NAME }}" \
--location "${{ env.REGION }}" \
dags trigger -- "${{ env.DAG_ID }}"