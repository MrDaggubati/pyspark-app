from pyspark.sql import DataFrame,SparkSession

class Extractor:
    """
       data extraction and other helper functions
    """

    def __init__(self, spark, filepaths):
        # Dict validation
        for key in ['sales', 'calendar', 'product', 'store']:
            if key not in filepaths.keys():
                print('Key ' + key + ' not available in filepaths.')
                raise ValueError('Key ' + key + ' not available in filepaths.')

        self.spark = spark
        self.filepaths = filepaths

    def _load_csv(self, filepath: str, delimiter=','):
        """
        extract file data and ceate dataframes for app data sources ; this returns a Spark Data Frame. takes file paths.
        """
        df_spark = self.spark.read \
            .format('csv') \
            .option("header", "true") \
            .option("delimiter", delimiter) \
            .option("encoding", 'utf-8') \
            .load(filepath)
        return df_spark

    def get_calendar_data(self) -> DataFrame:
        """
        Returns Spark Dataframe for transportation mode data
        """
        return self._load_csv(self.filepaths['calendar'])

    def get_sales_data(self) -> DataFrame:
        """
        Returns Spark Dataframe for sales data
        """
        return self._load_csv(self.filepaths['sales'])

    def get_store_data(self) -> DataFrame:
        """
        Returns Spark Dataframe for store data
        """
        return self._load_csv(self.filepaths['store'])

    def get_product_data(self) -> DataFrame:
        """
        Returns Spark Dataframe for product data
        """
        return self._load_csv(self.filepaths['product'])
