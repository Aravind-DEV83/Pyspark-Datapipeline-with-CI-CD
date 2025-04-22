import unittest
from pyspark.sql import SparkSession, Row
from pyspark.testing.utils import assertDataFrameEqual
from pyspark.sql.functions import to_timestamp, col
from transformations import total_ride_time, estimated_ride_time, average_speed, convert_to_timestamp

class PySparkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession. \
                builder. \
                appName("Integration Testing"). \
                config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS"). \
                config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"). \
                getOrCreate()


        cls.mock_df = cls.spark.createDataFrame(
            data = [
                Row(VendorID=1, tpep_pickup_datetime='2016-03-01 00:00:00', tpep_dropoff_datetime='2016-03-01 00:07:55', passenger_count=1, trip_distance=2.5, pickup_longitude=-73.97674560546875, pickup_latitude=40.765151977539055, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00426483154298, dropoff_latitude=40.74612808227539, payment_type=1, fare_amount=9.0, extra=0.5, mta_tax=0.5, tip_amount=2.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=12.35),
                Row(VendorID=1, tpep_pickup_datetime='2016-03-01 00:00:00', tpep_dropoff_datetime='2016-03-01 00:11:06', passenger_count=1, trip_distance=2.9, pickup_longitude=-73.98348236083984, pickup_latitude=40.767925262451165, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00594329833984, dropoff_latitude=40.7331657409668, payment_type=1, fare_amount=11.0, extra=0.5, mta_tax=0.5, tip_amount=3.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=15.35)
            ],
        ). \
        withColumn("tpep_pickup_datetime", to_timestamp(col("tpep_pickup_datetime"))). \
        withColumn("tpep_dropoff_datetime", to_timestamp(col("tpep_dropoff_datetime")))

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()


class IntegrationTest(PySparkTestCase):

    def test_transformations(self):

        input_file_path = 'gs://pyspark-job-omega-baton/tests/integration/tests_data/input_uber.csv'
        expected_output_path = 'gs:/pyspark-job-omega-baton/tests/integration/tests_data/expected_uber.csv'

        input_df = self.spark.read. \
                        format("csv"). \
                        option("header", "true"). \
                        option("inferSchema", "true"). \
                        load(input_file_path)
        
        print('Input DF: ')
        input_df.show()
        
        converted_df = convert_to_timestamp(input_df)

        ride_time_df = total_ride_time(converted_df)

        estimated_ride_time_df = estimated_ride_time(ride_time_df)

        result_df = average_speed(estimated_ride_time_df)

        print('Result DF: ')
        result_df.show()

        expected_df = self.spark.read. \
                    format("csv"). \
                    option("header", "true"). \
                    option("inferSchema", "true"). \
                    load(expected_output_path). \
                    orderBy('VendorId')

        print("Expected DF: ")
        expected_df.show()

        self.assertEqual(5, result_df.count())
        assertDataFrameEqual(result_df, expected_df)


if __name__ == "__main__":
    unittest.main()