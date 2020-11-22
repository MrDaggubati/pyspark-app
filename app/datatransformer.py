from pyspark.sql import SparkSession,DataFrame,SQLContext
import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.functions import concat, col, lit, expr, split, flatten, concat_ws, weekofyear, explode, dayofweek
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

        # split date into iso week weekday columns, similar to calendar.csv
        # content
        df_dummy_calendar = df_date_range.withColumn(
            "year", split(
                col("date"), "-").getItem(0)).withColumn(
            'dayofweek', dayofweek(
                df_date_range.date)).withColumn(
                    'iso_week', weekofyear(
                        df_date_range.date))

        # enrich with datekey
        df_dummy_calendar_upd = df_dummy_calendar.join(
            df_calendar_clean,
            (df_dummy_calendar.year == df_calendar_clean.datecalendaryear) & (
                df_dummy_calendar.iso_week == df_calendar_clean.ISOWEEK) & (
                df_dummy_calendar.dayofweek == df_calendar_clean.datecalendarday))

        # drop unnessary columns df_dummy_calendar_upd
        df_pseudo_calendar_csv = df_dummy_calendar_upd.drop(
            'ISOWEEK', 'datecalendarday', 'datecalendaryear', 'datecalendarday')

        # above innter join would drop all non  matching rows from the
        # calendar, bring them back again.
        df_dates_view = df_dummy_calendar.join(
            df_pseudo_calendar_csv,
            df_dummy_calendar["date"] == df_pseudo_calendar_csv["date"],
            "left_outer") .sort(
            df_dummy_calendar.date) .select(
            df_dummy_calendar.date,
            df_dummy_calendar.year,
            df_dummy_calendar.iso_week,
            df_pseudo_calendar_csv.datekey)

        print(" dates range got records ==> ",df_dates_view.count() )

        return df_dates_view

    def build_sales_facts(
            spark,
            df_sales:DataFrame,
            df_dates_view:DataFrame) -> DataFrame:
        """
        builds and returns df_sales_data.
        Args:
            takes df_sales dataframe, and a df_dates_view dataframe

        Returns:
            dataframe as df_sales_data (DataFrame): Spark DataFrame
        """

        df_sales.createOrReplaceTempView("sales_view")
        df_dates_view.createOrReplaceTempView("dates_view")

        df_sales_data = spark.sql(" select dates_view.* \
                                            ,sales_view.dateId,sales_view.storeId \
                                            ,sales_view.netSales,salesUnits \
                                            ,productId   \
                                    from dates_view \
                                    LEFT OUTER JOIN sales_view \
                                    ON (  \
                                    dates_view.datekey == sales_view.dateId  \
                                    ) \
                                    order by dates_view.date ASC \
                                    ")

        return df_sales_data

    def build_sales_prd_view(
            spark,
            df_sales_data:DataFrame,
            df_product_clean:DataFrame) -> DataFrame:
        """
        builds and returns an enhanced datframe of sales and product details.
        Args:
            takes df_sales_data dataframe, and a dff_product_clean dataframe

        Returns:
        df_sales_ddf_sales_and_prod_viewata (DataFrame): Spark DataFrame

        """

        df_sales_data.createOrReplaceTempView("sales_hist_view")

        df_product_clean.createOrReplaceTempView("products_view")

        df_sales_and_prod_view = spark.sql(
            "select sales_hist_view.date,sales_hist_view.year \
                                                ,sales_hist_view.iso_week,sales_hist_view.datekey \
                                                ,sales_hist_view.storeId \
                                                ,netSales,salesUnits,division,gender,category,sales_hist_view.productId     \
                                          from sales_hist_view   \
                                            LEFT OUTER JOIN products_view   \
                                            ON (   \
                                                products_view.productId == sales_hist_view.productId   \
                                             )  \
                                            order by sales_hist_view.date ASC  \
                                         ")

        return df_sales_and_prod_view

    def build_sales_store_view(spark,
                               df_sales_and_prod_view:DataFrame,
                               df_store_clean:DataFrame) -> DataFrame:
        """
        builds and returns an enhanced datframe of sales and stores details.
        Args:
            takes df_sales_and_prod_view dataframe, and a df_store_clean dataframe

        Returns:
        def_sales_info (DataFrame): Spark DataFrame

        """

        df_sales_and_prod_view.createOrReplaceTempView('sales_hub')
        df_store_clean.createOrReplaceTempView('store_dtls')

        def_sales_info = spark.sql(''' select
                            dates_view.date as DATE_ID,dates_view.year as YEARID,dates_view.iso_week as ISOWEEK,sales_hub.datekey,
                            country,division,category,gender,channel,netSales,salesUnits,productId,sales_hub.iso_week,sales_hub.year
                           ,store_dtls.country,store_dtls.channel,
                           division||'-'||country||"-"||category||"-"||gender||"-"||channel||"-"||sales_hub.year as uniqueid
                            from dates_view
                            LEFT OUTER JOIN sales_hub
                            ON (dates_view.date = sales_hub.date
                                )
                              LEFT OUTER JOIN store_dtls
                                 ON sales_hub.storeId = store_dtls.storeId
                        '''
                                   )
        return def_sales_info.na.fill({'netSales': 0, 'salesUnits': 0})
