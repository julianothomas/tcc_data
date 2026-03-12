import os
import sys
from pyspark.sql import SparkSession

print(">>> Python em uso:", sys.executable)

# Garante que Spark use este mesmo Python da venv
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = SparkSession.builder \
    .appName("teste_spark") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

print(">>> SparkSession criada!")

df = spark.createDataFrame(
    [(1, "a"), (2, "b"), (3, "c")],
    ["id", "letra"]
)

print(">>> Mostrando DataFrame:")
df.show()

print(">>> Encerrando Spark...")
spark.stop()
print(">>> fim do script")
