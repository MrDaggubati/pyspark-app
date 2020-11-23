from __future__ import print_function
import os
import sys
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession,DataFrame

from dataextractor import Extractor
from datasanitizer import Sanitizer
from datatransformer import Transformer
from validatiors import Validator
from consumption import ConsumptionReport

import miniostore as ms

def create_spark_session():

    spark = SparkSession \
        .builder \
        .appName("ConsumptionReport") \
        .getOrCreate()

    # sc = spark.sparkContext
    print(spark.sparkContext.getConf().getAll())

    return spark

    # spark.conf.get("spark.sql.crossJoin.enabled")


def extract(spark):
    """
    Extracts data from csv files
    """
    
    try:
        pass
        filepaths = {
           'sales': 'file:///app/data/sales.csv',
           'product': 'file:///app/data/product.csv',
           'calendar': 'file:///app/data/calendar.csv',
           'store': 'file:///app/data/store.csv'
        }
       
        extractor = Extractor(spark, filepaths)

        df_calendar = extractor.get_calendar_data()
        df_sales = extractor.get_sales_data()
        df_product = extractor.get_product_data()
        df_store = extractor.get_store_data()

        return df_calendar, df_sales, df_product, df_store
    except Exception as csv_file_read_error:
        print(csv_file_read_error)
        raise 
    # except OSError as e:
    # if e.errno == errno.ENOENT:
    #     logger.error('File not found')
    # elif e.errno == errno.EACCES:
    #     logger.error('Permission denied')
    # else:
    #     logger.error('Unexpected error: %d', e.errno)
def load(self):
    """
    OPTIONAL : data persistence; either in file store or data store
    """
    pass


def validate(
        spark,
        df_calendar:DataFrame,
        df_sales:DataFrame,
        df_store:DataFrame):
    """
    Validate the data loaded into the filestore /datawarhouse
    """

    validator = Validator(spark)

    assert(validator.contain_data(df_calendar))
    assert(validator.contain_data(df_sales))
    assert(validator.contain_data(df_store))
    assert(validator.contain_data(df_product))


if __name__ == "__main__":


    # def ringup():
    #      try:
    #          ms.Storeitminio.mintest()
    #      except Exception as minioerrors:
    #          print('oops minio might have got dies on ou ',minioerrors)  

    # ringup()
    # print('die local dev environment loading into minio ..  ---------------------------------- ')
    # raise sys.exit(0)

    spark = create_spark_session()

    df_calendar, df_sales, df_product, df_store = extract(spark)

    # clean
    df_calendar_clean = Sanitizer.clean_calendar_data(df_calendar)
    df_product_clean = Sanitizer.clean_product_data(df_product)
    df_store_clean = Sanitizer.clean_store_data(df_store)

    from_date = "2018-01-01"
    to_date = "2020-01-20"
    df_dates_view = Transformer.build_calendar(spark,from_date,to_date, df_calendar_clean)
     
    print(df_dates_view.count())

    df_sales_data = Transformer.build_sales_facts(spark, df_sales, df_dates_view)
    # enrich sales data further with product details
    df_sales_and_prod_view = Transformer.build_sales_prd_view(spark,df_sales_data, df_product_clean)

    # join sales and store details
    df_sales_info = Transformer.build_sales_store_view(spark,df_sales_and_prod_view, df_store_clean)

    # genarate consumption.json report
    ConsumptionReport.gen_consumption_report(spark,df_dates_view, df_sales_info)