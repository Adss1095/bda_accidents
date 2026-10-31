# Big Data Analytics for Road Accident Analysis (HDFS + Hive + Spark)

- `app.py` – Streamlit dashboard; `analysis.py` – cleaning/aggregation (pandas mirror of the Spark logic)
- `hive/queries.hql` – Hive table + HiveQL queries; `spark/spark_analysis.py` – PySpark job
- `generate_sample_data.py` → `data/accidents_sample.csv` (**synthetic** demo data)

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Deploy (Streamlit Community Cloud, free)
1. Push this folder to a GitHub repo. 2. share.streamlit.io → New app → pick repo, main file `app.py`. 3. Deploy; you get the public link.

## Hadoop commands
    hdfs dfs -mkdir -p /data/road_accidents
    hdfs dfs -put data/accidents_sample.csv /data/road_accidents/accidents.csv
    hive -f hive/queries.hql
    spark-submit spark/spark_analysis.py
