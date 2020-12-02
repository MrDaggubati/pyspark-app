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
            df_consumption_info) -> DataFrame:
        """
        generates a json report for df_consumption_info data .
        Args:
            takes df_consumption_info dataframe

        Returns:
            nothing, but stores json report for the same.

        issues:
           basically, this is to massag data with those missing week data, ideally. Typical DWH would have all data for all 53 ISO Weeks
           and , but here in the sample data , that was mising, making it a mess to go around to invest those missing records

        """
        df = df_consumption_info.alias("df")
        print("************************************************************************")
        print(df.count())    

        df2 = df.select("*",F.concat_ws('-',df.division,df.country,df.category,df.gender,df.channel,df.year).alias("uniqueid"))

        consumption_report = df2.select(
            'uniqueid',
            "division",
            "gender",
            "category",
            "country",
            "channel",
            "year",
            F.struct(
                F.col('WeekOfYear'),
                F.col("AggSalesUnits")).alias("SalesUnits"),
            F.struct(
                F.col('WeekOfYear'),
                F.col("AggNetSales")).alias("NetSales"))

        consumption_report.toJSON()

        # consumption_report.printSchema
        # here in this code base this file is going to save into minio docker volume, an s3 compatible object store
        consumption_report.write.partitionBy("uniqueid").mode('overwrite').json("/data/consumption", encoding='UTF-8')

    
    # def ringup():
    #     try:
    #         ms.Storeitminio.mintest()
    #     except Exception as minioerrors:
    #         print('oops minio might have got dies on ou ',minioerrors)    
    