val iot_df = spark.read.format("CSV").option("header", "true").option("mode", "DROPMALFORMED").load(args(0))
val sorted_iot_df = iot_df.orderBy(asc("cca2"), asc("timestamp"))
sorted_iot_df.write.format("csv").save(args(1))
