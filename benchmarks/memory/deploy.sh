project=`gcloud config get-value project 2> /dev/null`
name=benchmark-memory
folder=mapper
region=us-central1
root_path=../..

# Copy shared resources in
cp -r $root_path/src/knn $folder

# Submit build from within subdirectory
gcloud config set builds/use_kaniko True
(cd $folder && gcloud builds submit --tag gcr.io/$project/mihir-$name)

# Remove shared resources
rm -rf $folder/knn

# Deploy Cloud Run handler (both 1 and 2 vCPU versions for this benchmark)
# gcloud run deploy mihir-$name-1 --image gcr.io/$project/mihir-$name --platform managed --concurrency 1 --cpu 1 --max-instances 1000 --memory 2Gi --timeout 900 --region $region --allow-unauthenticated
gcloud run deploy mihir-$name-2 --image gcr.io/$project/mihir-$name --platform managed --concurrency 1 --cpu 2 --max-instances 1000 --memory 2Gi --timeout 900 --region $region --allow-unauthenticated
