FROM public.ecr.aws/emr-serverless/spark/emr-6.15.0:latest

# FROM 117819748843.dkr.ecr.us-east-1.amazonaws.com/emr-serverless:latest

USER root

COPY ./src/requirements.txt ./requirements.txt

COPY ./dist/* ./dist/

# RUN yum install gstreamer-1.0 gstreamer1.0-dev

# install python 3
# RUN yum install -y gcc openssl-devel bzip2-devel libffi-devel tar gzip wget make
# RUN wget https://www.python.org/ftp/python/3.9.0/Python-3.10.0.tgz && \
#     tar xzf Python-3.10.0.tgz && cd Python-3.9.0 && \
#     ./configure --enable-optimizations && \
#     make altinstall


RUN python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 -m pip install --no-cache-dir ./dist/*

# mkdir -p ~/miniconda3
# wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
# bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
# rm -rf ~/miniconda3/miniconda.sh

# EMRS will run the image as hadoop
USER hadoop:hadoop

# ENTRYPOINT []