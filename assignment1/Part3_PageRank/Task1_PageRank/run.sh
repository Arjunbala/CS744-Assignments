hadoop fs -rm -r $2
sleep 5
echo $1
echo $2
echo $3
echo $4
echo $5

#cat /proc/net/dev >> MasterNetWorkStatsBefore$5
#cat /proc/diskstats >> MasterDiskStatsBefore$5

#ssh follower-1 cat /proc/net/dev >>   F1NetWorkStatsBefore$5
#ssh follower-1 cat /proc/diskstats >> F1DiskStatsBefore$5

#ssh follower-2 cat /proc/net/dev >>   F2NetWorkStatsBefore$5
#ssh follower-2 cat /proc/diskstats >> F2DiskStatsBefore$5

#ssh follower-3 cat /proc/net/dev >>   F3NetWorkStatsBefore$5
#ssh follower-3 cat /proc/diskstats >> F3DiskStatsBefore$5



sleep 2

spark-shell -i PageRank_partition.scala --conf spark.driver.args="$1 $2 $3 $4 $5"

sleep 2

#cat /proc/net/dev >> MasterNetworkStatsAfter$5
#cat /proc/diskstats >> MasterDiskStatsAfter$5


#ssh follower-1 cat /proc/net/dev >>   F1NetWorkStatsAfter$5
#ssh follower-1 cat /proc/diskstats >> F1DiskStatsAfter$5

#ssh follower-2 cat /proc/net/dev >>   F2NetWorkStatsAfter$5
#ssh follower-2 cat /proc/diskstats >> F2DiskStatsAfter$5

#ssh follower-3 cat /proc/net/dev >>   F3NetWorkStatsAfter$5
#ssh follower-3 cat /proc/diskstats >> F3DiskStatsAfter$5
