from pyspark.sql import SparkSession,DataFrame,SQLContext
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.functions import concat, col, lit, expr, split, flatten, concat_ws, weekofyear, explode, dayofweek,min, ceil, count, first, row_number
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, FloatType, ArrayType

from datetime import datetime, date, time, timedelta
from itertools import groupby
import json

from datasanitizer import Sanitizer


class Transformer:
    """
        Performs the cleaning and transformation for the data
    """

    def __init__(self,spark):
        self.spark = spark

    def build_calendar(
        spark,
        fromdate: str,
        todate: str,
        df_calendar_clean:DataFrame
    ) -> DataFrame:
        """
        builds and returns a dummy dates calendar
        Args:
            fromdate,todate in format: "2018-01-01") and ,df_calendar_clean

        Returns:
            df (DataFrame): Spark DataFrame
        """
        querystring = "select sequence(to_date('{0}'),to_date('{1}'),interval 1 day) as date".format(fromdate,todate)

        # derive a pseudo date range
        df_date_range = spark.sql(querystring).withColumn("date", explode(col("date")))

        # split date into iso week weekday columns, similar to calendar.csv , but calendar.csv has weeks grnaularity at quarterly level
        # content
        df_dummy_calendar = df_date_range.withColumn(
            "year", split(
                col("date"), "-").getItem(0)).withColumn(
            'calendarDay', dayofweek(
                df_date_range.date)).withColumn(
                    'iso_week', weekofyear(
                        df_date_range.date))
       
        # get datekey and iso week number from  calendar.csv
        week1count=spark.createDataFrame(df_calendar_clean.orderBy(col("datekey")).head(7)).groupBy("weeknumberofseason").agg(first("datekey").alias("datekey"),count("weeknumberofseason").alias("cntweekone")).orderBy("datekey").first()["cntweekone"]
        windowSpec  = Window.partitionBy().orderBy("datekey")
        df_calendar_csv_upd = df_calendar_clean.select("*",(concat(lit("W"),ceil((row_number().over(windowSpec)-week1count)/7)+1)).alias("WeekOfYear"))
      
        # # enrich with datekey
        # df_dummy_calendar_upd = df_dummy_calendar.join(
        #     df_calendar_csv_upd,
        #     (df_dummy_calendar.year == df_calendar_csv_upd.datecalendaryear) & (
        #         df_dummy_calendar.iso_week == df_calendar_csv_upd.WeekOfYear) & (
        #         df_dummy_calendar.calendarDay == df_calendar_csv_upd.datecalendarday))
        
      
        # returning df_calendar_csv_upd as is without comparing with the other dummy calendar.
   
        # drop unnessary columns df_dummy_calendar_upd
        return  df_calendar_csv_upd.withColumnRenamed('datecalendaryear', 'year')  #.drop( 'ISOWEEK','datecalendaryear', 'datecalendarday')
