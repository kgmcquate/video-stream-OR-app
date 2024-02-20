FROM public.ecr.aws/emr-serverless/spark/emr-6.15.0:latest

# FROM 117819748843.dkr.ecr.us-east-1.amazonaws.com/emr-serverless:latest

USER root

COPY ./src/requirements.txt ./requirements.txt

COPY ./dist/* ./dist/

RUN python3 -m pip install -r requirements.txt && \
    python3 -m pip install ./dist/*

# EMRS will run the image as hadoop
USER hadoop:hadoop
