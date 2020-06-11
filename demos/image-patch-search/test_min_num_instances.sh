branch=`git rev-parse --abbrev-ref HEAD`
project=`gcloud config get-value project 2> /dev/null`
name=spatial-search
url=https://mihir-spatial-search-min-num-instances-g6rwrca4fq-uc.a.run.app

gcloud alpha run deploy mihir-$name-$branch --image gcr.io/$project/mihir-$name-$branch --platform managed --concurrency 1 --cpu 1 --max-instances 1000 --memory 2Gi --timeout 900 --region us-central1 --allow-unauthenticated --min-instances=1000
pipenv run python benchmark.py -m $url results/$1.json
gcloud alpha run deploy mihir-$name-$branch --image gcr.io/$project/mihir-$name-$branch --platform managed --concurrency 1 --cpu 1 --max-instances 1000 --memory 2Gi --timeout 900 --region us-central1 --allow-unauthenticated --min-instances=0
pipenv run python make_graphs.py -b $1.json
