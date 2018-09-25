// Get the arguments
val args = sc.getConf.get("spark.driver.args").split("\\s+")

// Load the CSV from HDFS into the dataframe
val iot_df = spark.read.format("CSV").option("header", "true").option("mode", "DROPMALFORMED").load(args(0))

//Apply the specified sorting by column
val sorted_iot_df = iot_df.orderBy(asc("cca2"), asc("timestamp"))

// Save the output into HDFS
sorted_iot_df.write.format("csv").save(args(1))
System.exit(0)
