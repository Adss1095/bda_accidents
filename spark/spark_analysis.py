from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, initcap, trim, to_timestamp, hour, month, year, concat_ws

spark = SparkSession.builder.appName("RoadAccidentAnalysis").getOrCreate()

df = (spark.read.option("header", True)
      .csv("hdfs:///data/road_accidents/accidents.csv"))

for c in ["district", "severity", "weather_condition", "road_surface", "vehicle_type"]:
    df = df.withColumn(c, initcap(trim(col(c))))

clean_df = (df.dropDuplicates()
            .filter(col("district").isNotNull() & col("severity").isNotNull())
            .withColumn("ts", to_timestamp(concat_ws(" ", col("accident_date"), col("accident_time"))))
            .filter(col("ts").isNotNull())
            .withColumn("year", year("ts")).withColumn("month", month("ts")).withColumn("hour", hour("ts")))

def summarise(c):
    out = clean_df.groupBy(c).agg(count("*").alias("accident_count")).orderBy(col("accident_count").desc())
    out.show()
    out.write.mode("overwrite").option("header", True).csv(f"hdfs:///output/accidents_by_{c}")

for c in ["district", "severity", "weather_condition", "road_surface", "vehicle_type", "hour", "month", "year"]:
    summarise(c)

spark.stop()
