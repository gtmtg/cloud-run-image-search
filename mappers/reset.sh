if [[ $# -ne 1 ]]; then
    echo "Usage: ./deploy.sh [subdir]"
    exit 1
fi

branch=`git rev-parse --abbrev-ref HEAD`
project=`gcloud config get-value project 2> /dev/null`
folder=`echo $1 | sed 's:/*$::'`
name=mihir-$folder-$branch
region=us-central1

# Deploy Cloud Run handler
gcloud run deploy $name --image gcr.io/$project/$name --platform managed --concurrency 1 --cpu 1 --max-instances 1000 --memory 2Gi --timeout 900 --region $region --allow-unauthenticated
