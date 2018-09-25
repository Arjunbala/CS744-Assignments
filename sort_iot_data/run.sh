echo "Hello, "$USER". I am here to help you sort the data you have from an IoT dataset"

while true
do
    echo -n "Would you like to run the job using Scala or Python?Select your option (S/P) and press [ENTER]:"
    read option
    if [ "$option" = "S" ] || [ "$option" = "s" ] || [ "$option" = "p" ] || [ "$option" = "P" ]; then
        break
    else
        echo "Please try again and enter a valid option."
    fi
done

echo -n "Enter the name of the input file and press [ENTER]:"
read input_file
echo -n "Enter the name of the output file and press [ENTER]:"
read output_file

start_time="$(date -u +%s)" #Note start time
if [ "$option" = "S" ] || [ "$option" = "s" ]; then
    # start up in Scala
    while true
    do
        echo -n "Would you like to run using RDDs or Dataframes?Select your option (R/D) and press [ENTER]:"
        read scala_option
        if [ "$option" = "R" ] || [ "$option" = "r" ]; then
            spark-shell -i sorting_iot_rdd.scala --conf spark.driver.args="$input_file $output_file"
            break
        elif [ "$option" = "D" ] || [ "$option" = "d" ]; then
            spark-shell -i sort_iot_data.scala --conf spark.driver.args="$input_file $output_file"
            break
        else
            echo "Please enter a valid option and try again."
        fi
    done
else
    # start up in Python
    spark-submit sort_iot_data.py -i $input_file -o $output_file
fi
end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Job done in $elapsed seconds"
