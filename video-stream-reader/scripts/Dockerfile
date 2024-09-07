FROM apache/spark:3.5.2-scala2.12-java11-ubuntu
USER root
RUN apt-get update && apt-get install -y wget xz-utils && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-7.0.2-arm64-static.tar.xz && \
    tar -xvf ffmpeg-7.0.2-arm64-static.tar.xz && \
    mv ffmpeg-7.0.2-arm64-static/ ffmpeg/ && \
    rm ffmpeg-7.0.2-arm64-static.tar.xz && \
    chown -R root.root ffmpeg/ && \
    cp ffmpeg/ffmpeg /usr/bin/ffmpeg && \
    cp ffmpeg/ffprobe /usr/bin/ffprobe



#FROM public.ecr.aws/emr-serverless/spark/emr-7.2.0:latest
#
#USER root
#
#RUN yum install -y wget xz && \
#    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-7.0.2-arm64-static.tar.xz && \
#    tar -xvf ffmpeg-7.0.2-arm64-static.tar.xz && \
#    mv ffmpeg-7.0.2-arm64-static/ ffmpeg/ && \
#    rm ffmpeg-7.0.2-arm64-static.tar.xz && \
#    chown -R root.root ffmpeg/ && \
#    cp ffmpeg/ffmpeg /usr/bin/ffmpeg && \
#    cp ffmpeg/ffprobe /usr/bin/ffprobe
#
#USER hadoop:hadoop
#
#ENTRYPOINT []
