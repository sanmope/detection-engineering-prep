# ── Como se vería este pipeline en PySpark (producción) ──

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("email-threat-detection").getOrCreate()

# 1. Leer eventos raw desde Kafka (stream en tiempo real)
raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "email.events")
    .load()
)

# 2. Parsear el JSON del evento
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType

schema = StructType() \
    .add("sender", StringType()) \
    .add("recipient", StringType()) \
    .add("domain", StringType()) \
    .add("num_urls", IntegerType()) \
    .add("has_attachment", IntegerType()) \
    .add("spf_pass", IntegerType()) \
    .add("timestamp", TimestampType())

parsed = raw_stream.select(
    F.from_json(F.col("value").cast("string"), schema).alias("e"),
    F.col("timestamp").alias("kafka_ts")
).select("e.*", "kafka_ts")

# 3. Calcular features agregadas por sender (ventana de 1 hora)
# Esto es lo que convierte eventos raw en filas del DataFrame de ML
window_1h = Window.partitionBy("sender") \
    .orderBy(F.col("kafka_ts").cast("long")) \
    .rangeBetween(-3600, 0)

features = parsed.withColumns({
    # Cuántos emails mandó este sender en la última hora
    "emails_last_hour": F.count("*").over(window_1h),
    
    # Tasa de URLs por email (alto = sospechoso)
    "avg_urls_1h": F.avg("num_urls").over(window_1h),
    
    # % de emails que fallaron SPF en la última hora
    "spf_fail_rate": (1 - F.avg("spf_pass")).over(window_1h),
    
    # Cuántos destinatarios distintos contactó (muchos = spam/phishing)
    "unique_recipients_1h": F.approx_count_distinct("recipient").over(window_1h),
})

# 4. Escribir features a S3 para batch ML, o directo al modelo
features.writeStream \
    .format("parquet") \
    .option("path", "s3://security-features/email/") \
    .option("checkpointLocation", "s3://checkpoints/email/") \
    .outputMode("append") \
    .trigger(processingTime="1 minute") \
    .start()