import json, fastavro

raw_image_avro_schema = fastavro.parse_schema(json.loads("""
        {
            "type": "record",
            "name": "sampleRecord",
            "doc": "Sample schema to help you get started.",
            "fields": [
                {
                  "name": "source_name",
                  "type": "string",
                  "doc": "source of the video, for example, youtube"
                },
                {
                    "name": "video_stream_id",
                    "type": "string",
                    "doc": "id for video stream taken from source"
                },
                {
                    "name": "frame_ts",
                    "type": "string",
                    "doc": "timestamp of when the frame was initially ingested",
                    "default": ""
                },
                {
                    "name": "jpeg_image",
                    "type": "bytes",
                    "doc": "jpeg image"
                },
                {
                    "name": "metadata_json",
                    "type": "string",
                    "doc": "Any additional information in json format"
                }
            ]
        }
        """))


      # "items": {
      #   "type": "array",
      #   "items": {
      #     "type": "float"
      #   }
      # }

processed_image_avro_schema = fastavro.parse_schema(json.loads("""
{
  "type": "record",
  "name": "sampleRecord",
  "doc": "Sample schema to help you get started.",
  "fields": [
    {
      "name": "source_name",
      "type": "string",
      "doc": "source of the video, for example, youtube"
    },
    {
      "name": "video_stream_id",
      "type": "string",
      "doc": "id for video stream taken from source"
    },
    {
      "name": "frame_ts",
      "type": "string",
      "doc": "timestamp of when the frame was initially ingested"
    },
    {
      "name": "detector_name",
      "type": "string",
      "doc": "name of algorithm used to detect objects"
    },
    {
      "name": "detector_version",
      "type": "string",
      "doc": "SemVer version of the detector"
    },
    {
      "name": "object_name",
      "type": "string",
      "doc": "type of object detected"
    },
    {
      "name": "object_bounding_boxes_json",
      "doc": "object bounding boxes in json format",
      "type": "string"
    },
    {
      "name": "jpeg_image",
      "type": "bytes",
      "doc": "jpeg image"
    },
    {
      "name": "metadata_json",
      "type": "string",
      "doc": "Any additional information in json format"
    }
  ]
  }"""))