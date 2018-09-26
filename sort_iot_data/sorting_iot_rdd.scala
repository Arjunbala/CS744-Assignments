// Get the input arguments
val args = sc.getConf.get("spark.driver.args").split("\\s+")

// First, load in the data from HDFS
var raw_data = sc.textFile(args(0))

// We need to remove the CSV header which has the column names
val header = raw_data.first()
raw_data = raw_data.filter(line => line != header)

val header_append = sc.parallelize(header.split("\\s+"),1)

// Since the data is in CSV format, we split into an Array of Strings
val split_data = raw_data.map(line => line.split(","))

// Now, we construct a key/value pair in the format <(cca2,timestamp),entire entry>
val indexed_data = split_data.map(array => ((array(2),array(14)),array))

// Now sort by key. The secondary sorting by timestamp will be taken care of automatically
val sorted_data = indexed_data.repartition(4).sortByKey().persist()


// Remove the keys since we now only need the original entries in CSV format.
val final_data = sorted_data.map{case (a,b) => b.mkString(",")}

val final_data_to_write = sc.union(header_append,final_data)

// Save it back to HDFS and exit
final_data_to_write.saveAsTextFile(args(1))
System.exit(0)
