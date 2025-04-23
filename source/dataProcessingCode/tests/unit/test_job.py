import unittest
from pyspark.sql import SparkSession, Row
from pyspark.testing.utils import assertDataFrameEqual
from pyspark.sql.functions import to_timestamp, col
from transformations import total_ride_time, estimated_ride_time, average_speed

class PySparkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession. \
                builder. \
                appName("Unit Testing"). \
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

class TestTransformation(PySparkTestCase):

    def test_total_ride_time(self):
        expected_result = self.spark.createDataFrame(
            data = [
                Row(VendorID=1, tpep_pickup_datetime="2016-03-01 00:00:00", tpep_dropoff_datetime="2016-03-01 00:07:55", passenger_count=1, trip_distance=2.5, pickup_longitude=-73.97674560546875, pickup_latitude=40.765151977539055, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00426483154298, dropoff_latitude=40.74612808227539, payment_type=1, fare_amount=9.0, extra=0.5, mta_tax=0.5, tip_amount=2.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=12.35, total_ride_time=475),
                Row(VendorID=1, tpep_pickup_datetime="2016-03-01 00:00:00", tpep_dropoff_datetime="2016-03-01 00:11:06", passenger_count=1, trip_distance=2.9, pickup_longitude=-73.98348236083984, pickup_latitude=40.767925262451165, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00594329833984, dropoff_latitude=40.7331657409668, payment_type=1, fare_amount=11.0, extra=0.5, mta_tax=0.5, tip_amount=3.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=15.35, total_ride_time=666)
            ]
        ). \
        withColumn("total_ride_time", col("total_ride_time").cast("double")). \
        withColumn("tpep_pickup_datetime", to_timestamp(col("tpep_pickup_datetime"))). \
        withColumn("tpep_dropoff_datetime", to_timestamp(col("tpep_dropoff_datetime")))

        result = total_ride_time(self.mock_df)

        self.assertEqual(2, result.count())
        assertDataFrameEqual(expected_result, result)

    def test_estimated_ride_time(self):

        expected_result = self.spark.createDataFrame(
            data = [
                Row(VendorID=1, tpep_pickup_datetime="2016-03-01 00:00:00", tpep_dropoff_datetime="2016-03-01 00:07:55", passenger_count=1, trip_distance=2.5, pickup_longitude=-73.97674560546875, pickup_latitude=40.765151977539055, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00426483154298, dropoff_latitude=40.74612808227539, payment_type=1, fare_amount=9.0, extra=0.5, mta_tax=0.5, tip_amount=2.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=12.35, total_estimated_ride_time=300.0),
                Row(VendorID=1, tpep_pickup_datetime="2016-03-01 00:00:00", tpep_dropoff_datetime="2016-03-01 00:11:06", passenger_count=1, trip_distance=2.9, pickup_longitude=-73.98348236083984, pickup_latitude=40.767925262451165, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00594329833984, dropoff_latitude=40.7331657409668, payment_type=1, fare_amount=11.0, extra=0.5, mta_tax=0.5, tip_amount=3.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=15.35, total_estimated_ride_time=348.0)
            ]
        ). \
        withColumn("tpep_pickup_datetime", to_timestamp(col("tpep_pickup_datetime"))). \
        withColumn("tpep_dropoff_datetime", to_timestamp(col("tpep_dropoff_datetime")))

        result = estimated_ride_time(self.mock_df)

        self.assertEqual(2, result.count())
        assertDataFrameEqual(result, expected_result)

    def test_average_speed(self):

        expected_result = self.spark.createDataFrame(
            data = [
                Row(VendorID=1, tpep_pickup_datetime="2016-03-01 00:00:00", tpep_dropoff_datetime="2016-03-01 00:07:55", passenger_count=1, trip_distance=2.5, pickup_longitude=-73.97674560546875, pickup_latitude=40.765151977539055, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00426483154298, dropoff_latitude=40.74612808227539, payment_type=1, fare_amount=9.0, extra=0.5, mta_tax=0.5, tip_amount=2.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=12.35, total_ride_time=475, average_speed=19.0),
                Row(VendorID=1, tpep_pickup_datetime="2016-03-01 00:00:00", tpep_dropoff_datetime="2016-03-01 00:11:06", passenger_count=1, trip_distance=2.9, pickup_longitude=-73.98348236083984, pickup_latitude=40.767925262451165, RatecodeID=1, store_and_fwd_flag="N", dropoff_longitude=-74.00594329833984, dropoff_latitude=40.7331657409668, payment_type=1, fare_amount=11.0, extra=0.5, mta_tax=0.5, tip_amount=3.05, tolls_amount=0.0, improvement_surcharge=0.3, total_amount=15.35, total_ride_time=666, average_speed=16.0)
            ]
        ). \
        withColumn("total_ride_time", col("total_ride_time").cast("double")). \
        withColumn("tpep_pickup_datetime", to_timestamp(col("tpep_pickup_datetime"))). \
        withColumn("tpep_dropoff_datetime", to_timestamp(col("tpep_dropoff_datetime")))

        ride_time_df = total_ride_time(self.mock_df)
        result = average_speed(ride_time_df)

        self.assertEqual(2, result.count())
        assertDataFrameEqual(expected_result, result)

if __name__ == "__main__":
    unittest.main()
