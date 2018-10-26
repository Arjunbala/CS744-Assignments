/////////////////////
//MiniGoogle  
//cmnd : spark-shell -i PageRank_partition.scala --conf spark.driver.args="inputFile outputFile iteration big/small partition"
//pray to God 
////////////////////

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import org.apache.spark.HashPartitioner

// for data cleaning 
def validLine(line:String, fileType:String) :   Boolean = {
    // if small file, check for "#"
    if (fileType.toLowerCase == "small")
        {
            if (line.startsWith("#"))
                return false
            else 
                return true
        }
    else //if(fileType.toLowerCase == "big")
        {
            // bigger file, check for ":" and "contains:"
        if(line.startsWith("The files"))
		return false    
	if (line.contains(":"))
                {
                    if (line.toLowerCase.contains("category:"))
                        return true
                    else 
                        return false
                }
         else
             return true
        }
}


//parser
def lineParser(line:String, fileType:String) : (String, String) = {

    if (fileType.toLowerCase == "small")
        {
            val buf = line.split("\\s+")
            return (buf(0).toLowerCase, buf(1).toLowerCase)
        }
    
    else //if (fileType.toLowerCase == "big")
        {
            val buf = line.split("\\t",2)
            //println(buf)
            return (buf(1).toLowerCase, buf(0).toLowerCase)
        }
    //else
      //  return ("NA", "NA")
}

//val conf = new SparkConf().setAppName("PageRank").setMaster("local")
//new SparkContext(conf)

val args = sc.getConf.get("spark.driver.args").split("\\s+")

// read dataset 
// filter according to 
var rawData = sc.textFile(args(0)).filter(line => validLine(line, args(3)))//.map((a,b) => (a.toLowerCase, b.toLowerCase))
//rawData.collect().foreach(println)


// parse each line of rawData
// (x,y) 
val edges = rawData.map(line => lineParser(line, args(3)))
//edges.collect().foreach(println)

// prepare rank for each node
// assign 1 for each node at the start 
// make it "var" as rank is going to get updated
// *** BUG Resolve : consider all nodes ***  
var rank = edges.keys.union(edges.values).distinct().map(k => (k,1.0))

//declare partiotioner
var partitioner = new HashPartitioner(partitions = args(4).toInt)

// adjacency list
val graph = edges.distinct().groupByKey().partitionBy(partitioner)

val totalCount = args(2).toInt

for (count <- 1 to totalCount)
{
    // join graph with ranks, to get the rank of node
    val graphRank = graph.join(rank)

    // get nodes and rank 
    val nodesRank = graphRank.values

    // divide rank equally among nodes 
    var rankContrib = nodesRank.flatMap{ case (urls, b)=> urls.map(url =>  (url, b*1.0/urls.size))}
    // sum rankContributions of each node
    rankContrib = rankContrib.reduceByKey((a:Double, b:Double) => a+b)

    // join again to make sure all nodes are there
    // even nodes with no inward edges
    val nrank = rank.leftOuterJoin(rankContrib)
    
    // b is option(double) 
    rank = nrank.map{
                        case (a,b) =>  
                        var contrib = b._2.getOrElse(0.0)
                        (a,0.15 + 0.85*contrib)
                    }.partitionBy(partitioner)

    //rank.collect().foreach(println)
}

// Write to HDFS
rank.saveAsTextFile(args(1))


println("The deed is done!")

System.exit(0)
