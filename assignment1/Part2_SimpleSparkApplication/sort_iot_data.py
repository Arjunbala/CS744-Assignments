from pyspark.context import SparkContext
from pyspark.sql import SQLContext
import sys, getopt

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   sc = SparkContext.getOrCreate()
   sqlContext = SQLContext(sc)
   iot_dataframes = sqlContext.read.format("CSV").option("header", "true").option("mode", "DROPMALFORMED").load(inputfile)
   sorted_iot_dataframes = iot_dataframes.sort(['cca2', 'timestamp'], ascending=[True, True])
   sorted_iot_dataframes.write.csv(outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
