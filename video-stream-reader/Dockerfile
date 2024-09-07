FROM public.ecr.aws/emr-serverless/spark/emr-7.2.0:latest

# FROM 117819748843.dkr.ecr.us-east-1.amazonaws.com/emr-serverless:latest

USER root

RUN yum install -y wget xz && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-7.0.2-arm64-static.tar.xz && \
    tar -xvf ffmpeg-7.0.2-arm64-static.tar.xz && \
    mv ffmpeg-7.0.2-arm64-static/ ffmpeg/ && \
    rm ffmpeg-7.0.2-arm64-static.tar.xz && \
    chown -R root.root ffmpeg/ && \
    cp ffmpeg/ffmpeg /usr/bin/ffmpeg && \
    cp ffmpeg/ffprobe /usr/bin/ffprobe

# EMRS will run the image as hadoop
USER hadoop:hadoop
