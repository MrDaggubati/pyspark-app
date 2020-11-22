from pyspark.sql import SparkSession,DataFrame
import pyspark.sql.functions as F
from pyspark.sql.functions import col
import json
from datatransformer import Transformer
import miniostore as ms

class ConsumptionReport:
    """
    builds temp data or validates data thats supplied
    """

    def __init__(self, spark):
        self.spark = spark

    def gen_consumption_report(
            spark,
            df_dates_view:DataFrame,
            df_sales_info:DataFrame) -> DataFrame:
        """
        builds and returns df_sales_data.
        Args:
            takes df_dates_view dataframe, and a df_sales_info dataframe

        Returns:
            df_sales_data (DataFrame): Spark DataFrame

        issues:
           basically, this is to massag data with those missing week data, ideally. Typical DWH would have all data for all 53 ISO Weeks
           and , but here in the sample data , that was mising, making it a mess to go around to invest those missing records

        """

        # Here this is needed to get weeks from 01-53(typical year calendar)
        # provided sales data is incomlete and got dificult to get 53 week
        # views on it.

        MISSING_WEEKS = df_dates_view.select(
            'year', 'iso_week').drop_duplicates()
        condition = [MISSING_WEEKS.year == df_sales_info.year,
                     MISSING_WEEKS.iso_week == df_sales_info.ISOWEEK]
        viewlet = MISSING_WEEKS.join(
            df_sales_info,
            condition,
            "left_outer").select(
            "uniqueid",
            "country",
            "channel",
            MISSING_WEEKS.year,
            MISSING_WEEKS.iso_week,
            "netSales",
            "salesUnits",
            "division",
            "gender",
            "category")

        viewlet.createOrReplaceTempView('consumption_viewlet')
        sales_report_view = spark.sql('''
                                select uniqueid,division,gender,category,country,channel,year,iso_week
                                      ,sum(netSales) as netSales,sum(salesUnits) as salesUnits
                                from consumption_viewlet
                                group by uniqueid,division,gender,category,country,channel,year,iso_week
                                '''
                                      )

        consumption_report = sales_report_view.select(
            "uniqueid",
            "division",
            "gender",
            "category",
            "country",
            "channel",
            "year",
            'iso_week',
            F.struct(
                F.col('iso_week'),
                F.col("netSales")).alias("net_Sales"),
            F.struct(
                F.col('iso_week'),
                F.col("salesUnits"),
            ).alias("sales_units"))

        consumption_report.toJSON()

        # consumption_report.printSchema
        # here in this code base this file is going to save into minio docker volume, an s3 compatible object store
        consumption_report.write.partitionBy("uniqueid").mode(
            'overwrite').json("consumption/consumption", encoding='UTF-8')

    
    
    # def ringup():
    #     try:
    #         ms.Storeitminio.mintest()
    #     except Exception as minioerrors:
    #         print('oops minio might have got dies on ou ',minioerrors)    
    