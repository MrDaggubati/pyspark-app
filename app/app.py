from __future__ import print_function
import os
import sys
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession,DataFrame
from pyspark.sql.functions import lit, min, col, ceil, count, first, row_number, sum, coalesce, concat

from dependencies.spark import start_spark
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


def extract(spark,config,spark_files):
    """
    Extracts data from csv files
    """
    try:
        filepaths = {
                'sales': 'file:///data/sales.csv',
                'product': 'file:///data/product.csv',
                'calendar': 'file:///data/calendar.csv',
                'store': 'file:///data/store.csv'
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


def spark_steps(spark,log,config,spark_files):
    

    log.warn('spark batch job steps being executed')
    df_calendar, df_sales, df_product, df_store = extract(spark,config,spark_files)
    df_calendar_clean = Sanitizer.clean_calendar_data(df_calendar)
    df_product_clean = Sanitizer.clean_product_data(df_product)
    df_store_clean = Sanitizer.clean_store_data(df_store)
    df_sales_clean = Sanitizer.clean_sales_data(df_sales)

    log.warn('building calendar view')
    from_date = "2018-01-01"
    to_date = "2020-01-20"
    df_dates_view = Transformer.build_calendar(spark,from_date,to_date, df_calendar_clean)

    # df_store_clean.write.mode('overwrite').json("/data/output/store", encoding='UTF-8')
    # df_product_clean.write.mode('overwrite').json("/data/output/product", encoding='UTF-8')
    # df_sales_clean.write.mode('overwrite').json("/data/output/sale", encoding='UTF-8')
    # df_dates_view.write.mode('overwrite').json("/data/output/calendar", encoding='UTF-8')
    

    df_consumption_info = df_store_clean.join(df_product_clean,
            df_store_clean.Joinkey_store
            == df_product_clean.Joinkey_product).join(df_dates_view,
            df_store_clean.Joinkey_store
            == df_dates_view.Joinkey_calendar).join(df_sales_clean,
            (df_store_clean.storeId == df_sales_clean.storeId)
            & (df_dates_view.datekey == df_sales_clean.dateId)
            & (df_product_clean.productId == df_sales_clean.productId),
            how='left').groupBy(
        'country',
        'gender',
        'division',
        'category',
        'year',
        'WeekOfYear',
        'channel',
        ).agg(sum(coalesce('salesUnits', lit(0))).alias('AggSalesUnits'
              ), sum(coalesce('netSales', lit(0))).alias('AggNetSales'
              )).orderBy('country', 'gender', 'category', 'WeekOfYear')


    # # Genarate consumption.json report
    ConsumptionReport.gen_consumption_report(spark,df_consumption_info)

    return None

def main():
    """ this creates the context for the spark session.
    """
    # start Spark application and get Spark session, logger and config
    # here app_config to get specific values that are applicable for your application logic
    # use spark_Config for all other configs like log level, key spark config to be sued for this job
    spark, log, config , spark_files = start_spark(
        app_name='ConsumptionReport',
        files=['conf/app_config.json'], spark_config= ['conf/submit_config.json'])

    # log that main ETL job is starting
    log.warn('Spark_job is up-and-running')

    # execute your big data pipeline
    spark_steps(spark,log,config, spark_files)
    
    # log the success and terminate Spark application
    log.warn(' job exwcution  finished')
    spark.stop()
    return None    
if __name__ == "__main__":
    main()
