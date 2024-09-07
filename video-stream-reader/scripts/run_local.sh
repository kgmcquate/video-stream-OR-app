docker build . -t spark-ffmpeg:latest

docker run \
  -v $(pwd)/../:/opt/run/ \
  -e AWS_ACCESS_KEY_ID="`aws configure get default.aws_access_key_id`" \
  -e AWS_SECRET_ACCESS_KEY="`aws configure get default.aws_secret_access_key`" \
  -it spark_test \
  /opt/spark/bin/spark-submit \
  --master local[1] \
  --class com.kgmcquate.video.livestream.reader.Main \
  /opt/run/target/scala-2.12/video-stream-reader.jar


#  -v $(pwd)/img_temp/:/opt/spark/work-dir/ \
