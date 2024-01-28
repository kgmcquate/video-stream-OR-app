# video-stream-OR-app
Application for processing video streams and recognizing objects in them


# TODO
describe what's happening in video
give count of objects in video
record these over time in kafka
overlay box for object recognition


search for videos and add them to the stream

chunk up mp4 files and send over kafka

use confluent kafka

# Architecture
```mermaid
graph LR
    subgraph Website
        livestream-manager
    end

    subgraph DB
        livestreams
    end

    livestream-manager --> livestreams

    subgraph Airflow
        subgraph livestream-ingest
            ingester-controller
            ingester-controller --spins up --> livestream-ingester-1
            ingester-controller --spins up --> livestream-ingester-2
        end
    end

    livestreams -- reads periodically --> ingester-controller

    subgraph YouTube
        livestream-1
        livestream-2
    end

    livestream-1 --> livestream-ingester-1
    livestream-2 --> livestream-ingester-2

    subgraph Pulsar
        livestream-frames

    end

    livestream-ingester-1 --> livestream-frames
    livestream-ingester-2 --> livestream-frames

    


```