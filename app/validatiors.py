from pyspark.sql import DataFrame,SparkSession
import pyspark.sql.functions as F


class Validator:
    """
    Validates data located in warehouse/filestore/Even intermediary steps where such steps needs tobe done.
    Better to extend with pytest kind of test frameworks. -- WIP
    """

    def __init__(self, spark):
        self.spark = spark

    def contain_data(self, df:DataFrame) -> bool:
        # checks the record count
        return df.count() > 0
