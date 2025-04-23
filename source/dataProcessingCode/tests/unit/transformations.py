import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, to_timestamp, when, round

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')

def convert_to_timestamp(input_df: DataFrame) -> DataFrame:
    """Convert String to Timestamp
    
    Keyword arguments:
    :param df - Input DataFrame
    :return DataFrame
    """

    converted_df = input_df. \
        withColumn("tpep_pickup_datetime", to_timestamp(col("tpep_pickup_datetime"))). \
        withColumn("tpep_dropoff_datetime", to_timestamp(col("tpep_dropoff_datetime")))

    return converted_df


def total_ride_time(input_df: DataFrame) -> DataFrame:
    """Calucate the total time taken for the ride.

    Keyword arguments:
    :param df - Input DataFrame
    :return DataFrame
    """

    ride_time_df = input_df. \
                    withColumn("total_ride_time", when(
                        col("tpep_pickup_datetime") != col("tpep_dropoff_datetime"), 
                        round(col("tpep_dropoff_datetime").cast("long") - col("tpep_pickup_datetime").cast("double"), 2)
                    ).otherwise(0)
                    )
    return ride_time_df

def estimated_ride_time(input_df: DataFrame) -> DataFrame:
    """Calucate the estimated time taken for the ride.

    Keyword arguments:
    :param df - Input DataFrame
    :return DataFrame
    """
    avg_speed = 30

    estimated_df = input_df. \
                    withColumn("total_estimated_ride_time",
                        round(col("trip_distance") / avg_speed * 60 * 60)
                    )
    return estimated_df

def average_speed(input_df: DataFrame) -> DataFrame:
    """Calucate the average speed taken for the ride.

    Keyword arguments:
    :param df - Input DataFrame
    :return DataFrame
    """
    speed_df = input_df. \
                withColumn("average_speed", when(
                    col("total_ride_time")!=0,
                    round( (col("trip_distance") / col("total_ride_time")) * 3600)
                ).otherwise(0)
                )
    return speed_df
