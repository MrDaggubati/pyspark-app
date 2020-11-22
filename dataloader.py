from pyspark.sql import DataFrame

class Loader:
    """
    saves data into either datalakes or file stores ; 
    can be parquet or json or any format that is desired as created from spark dataframes
    """
    
    def __init__(self, spark_session):
      self.spark = spark_session

    def _load_data(self, df:DataFrame, path:str):
        """
        Loads provided Spark DataFrame into specified path. Data is saved as json for consumption report

        Args:
            df (DataFrame): Sparrk DataFrame to be loaded
            path (str): Path to load the DataFrame
        """
        df.write.mode('overwrite').json(path)

    
    