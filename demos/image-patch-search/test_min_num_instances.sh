if [[ $# -ne 1 && $# -ne 2 ]]; then
    echo "Usage: ./test_min_num_instances.sh [experiment name] [sleep time (optional, default 0)]"
    exit 1
fi

label=$1
sleep_for=${2:-0}

branch=`git rev-parse --abbrev-ref HEAD`
project=`gcloud config get-value project 2> /dev/null`
name=spatial-search
url=https://mihir-spatial-search-min-num-instances-g6rwrca4fq-uc.a.run.app

START_TIME=`python3 -c 'import time;print(time.time())'`
gcloud alpha run deploy mihir-$name-$branch --image gcr.io/$project/mihir-$name-$branch --platform managed --concurrency 1 --cpu 1 --max-instances 1000 --memory 2Gi --timeout 900 --region us-central1 --allow-unauthenticated --min-instances=1000
SLEEP_TIME=`python3 -c 'import time;print(time.time())'`
sleep $sleep_for
BENCHMARK_TIME=`python3 -c 'import time;print(time.time())'`
pipenv run python benchmark.py -m $url results/$label.json -s $START_TIME
SHUTDOWN_TIME=`python3 -c 'import time;print(time.time())'`
gcloud alpha run deploy mihir-$name-$branch --image gcr.io/$project/mihir-$name-$branch --platform managed --concurrency 1 --cpu 1 --max-instances 1000 --memory 2Gi --timeout 900 --region us-central1 --allow-unauthenticated --min-instances=0
END_TIME=`python3 -c 'import time;print(time.time())'`

echo "Deploy start time:                   $START_TIME"     | tee results/$label.log
echo "Deploy end + sleep start time:       $SLEEP_TIME"     | tee -a results/$label.log
echo "Sleep end + benchmark start time:    $BENCHMARK_TIME" | tee -a results/$label.log
echo "Benchmark end + shutdown start time: $SHUTDOWN_TIME"  | tee -a results/$label.log
echo "Shutdown end time:                   $END_TIME"       | tee -a results/$label.log
