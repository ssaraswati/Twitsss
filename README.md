# Scrapes tweets and stores them in s3

set environment variables


export AWS_REGION=us-east-1
export AWS_BUCKET_NAME=tweets
export AWS_BUCKET_PREFIX=melbourne

export TWITTER_CONSUMER_KEY=asdf1234
export TWITTER_CONSUMER_SECRET=asdf1234
export TWITTER_ACCESS_KEY=asdf1234
export TWITTER_ACCESS_SECRET=asdf1234

BOUNDING_BOX="144.0,-38.3,145.7,-37.5"


aws ecs run-task --launch-type FARGATE --cluster BlogCluster --task-definition blog --network-configuration "awsvpcConfiguration={subnets=[subnet-b563fcd3]}"