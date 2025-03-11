from typing import Optional, Sequence, Dict, Any
import logging
import argparse

from pyspark.sql import SparkSession, DataFrame
from transformations import convert_to_timestamp, total_ride_time, average_speed,estimated_ride_time

import constants as constants

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')

def parse_args(args: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        f'--{constants.GCS_INPUT_LOCATION}',
        required=True
    )
    parser.add_argument(
        f'--{constants.PROJECT_ID}',
        required=True
    )
    parser.add_argument(
        f'--{constants.GCS_BQ_OUTPUT_TABLE}',
        required=True
    )
    parser.add_argument(
        f'--{constants.GCS_BQ_TEMP_BUKCET}',
        required=True
    )

    known_args: argparse.Namespace
    known_args, _ = parser.parse_known_args(args)

    return vars(known_args)


def create_spark_session(bq_temp_bucket: str) -> SparkSession:

    spark = SparkSession.builder. \
                    appName("GCS to BQ Pipeline"). \
                    config("temporaryGcsBucket", bq_temp_bucket). \
                    config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS"). \
                    config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"). \
                    getOrCreate()

    logging.info("Spark Session Initiated sucessfully")
    return spark

def data_load(spark: SparkSession, path: str) -> DataFrame:
    """Load Data from GCS

    :param spark - Spark Session Object
    :return DataFrame
    """
    input_df = spark.read. \
            format("csv"). \
            option("header", "true"). \
            option("inferSchema", "true"). \
            load(path)

    return input_df

def data_write(output_df: DataFrame, project_id: str, bq_output_table: str):
    """"Write Data to BigQuery

    Keyword arguments:
    :param df - DataFrame
    :return None
    """

    output_df.write.format("bigquery"). \
            option("table",f'{project_id}.{bq_output_table}'). \
            mode("overwrite"). \
            save()
    logging.info("Sucesfully upated data to BQ.")

def main():
    """Pipeline Script Defination

    :return: None
    """

    #Arguments
    args = parse_args()
    input_location: str = args[constants.GCS_INPUT_LOCATION]
    project_id: str = args[constants.PROJECT_ID]
    bq_output_table: str = args[constants.GCS_BQ_OUTPUT_TABLE]
    bq_temp_bucket: str = args[constants.GCS_BQ_TEMP_BUKCET]

    spark = create_spark_session(bq_temp_bucket)
    input_df = data_load(spark, input_location)

    logging.info("transformations -- IN ")
    converted_df = convert_to_timestamp(input_df)

    ride_time_df = total_ride_time(converted_df)

    estimated_ride_time_df = estimated_ride_time(ride_time_df)

    average_speed_df = average_speed(estimated_ride_time_df)

    average_speed_df. \
            select(
                "trip_distance", "total_ride_time", "total_estimated_ride_time", "average_speed"
            ). \
            show()
    logging.info("transformations -- OUT")

    data_write(average_speed_df, project_id, bq_output_table)

    spark.stop()
    logging.info("Job finshed")


if __name__ == "__main__":
    main()
