from pyspark.sql import SparkSession,DataFrame
import pyspark.sql.functions as F


class Sanitizer:
    """
        Performs the cleaning and transformation for the data
    """

    def __init__(self, spark):
        self.spark = spark


    @staticmethod
    def clean_calendar_data(df_calendar:DataFrame) -> DataFrame:
        """
        Cleans df_caelendar. pads characters and drops the duplicate columns.. etc..
        dataextractor.py function get_calendar_data: should invoke this after csv extract
        Args:
            df_calendar (DataFrame): Spark Dataframe with calendar data

        Returns:
            DataFrame: Spark Dataframe with cleaned calendar data
        """
        df = df_calendar.select(
              F.lpad(
                df_calendar['weeknumberofseason'],
                2,
                '0').alias('weeknumberofseason'),
            'datecalendaryear',
            'datecalendarday',
            'datekey')


        df_calendar_clean = df.select("*",F.lit("1").alias("Joinkey_calendar"))
        return df_calendar_clean

    @staticmethod
    def clean_product_data(df_product:DataFrame) -> DataFrame:
        """
        Cleans df_product. pads characters and drops the duplicate columns.. etc..
        dataextractor.py function can be called after csv read
        should invoke this after csv extract
        Args:
            df_product (DataFrame): Spark Dataframe with product data

        Returns:
            DataFrame: Spark Dataframe with cleaned product data
        """

        df_product_clean = df_product.select("*",F.lit("1").alias("Joinkey_product")).withColumnRenamed(
            'productid', 'productId')

        return df_product_clean

    @staticmethod
    def clean_store_data(
            df_store:DataFrame) -> DataFrame:
        """
        Cleans df_store. pads characters and drops the duplicate columns.. etc..
        dataextractor.py function can/should be called after csv read
        Args:
            df_store (DataFrame): Spark Dataframe with store data

        Returns:
            DataFrame: Spark Dataframe with cleaned store data
        """
        df_store_clean = df_store.select("*",F.lit("1").alias("Joinkey_store")).withColumnRenamed(
            'storeid', 'storeId').withColumn(
            "country", F.trim(
                df_store.country))


        return df_store_clean

    @staticmethod
    def clean_sales_data(
            df_sales:DataFrame) -> DataFrame:
        """
        Cleans df_sales. pads characters and drops the duplicate columns.. etc..
        Args:
            df_sales (DataFrame): Spark Dataframe with store data

        Returns:
            DataFrame: Spark Dataframe with cleaned store data
        """

        df_sales_clean = df_sales.select("*",F.lit("1").alias("Joinkey_sales"))

        return df_sales_clean