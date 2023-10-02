raw_image_avro_schema = """
        {
            "type": "record",
            "name": "sampleRecord",
            "doc": "Sample schema to help you get started.",
            "fields": [
                {
                    "name": "video_stream_id",
                    "type": "string",
                    "doc": "id for video stream taken from source"
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
        """


      # "items": {
      #   "type": "array",
      #   "items": {
      #     "type": "float"
      #   }
      # }

processed_image_avro_schema = """
{
  "type": "record",
  "name": "sampleRecord",
  "doc": "Sample schema to help you get started.",
  "fields": [
    {
      "name": "video_stream_id",
      "type": "string",
      "doc": "id for video stream taken from source"
    },
    {
      "name": "detector_name",
      "type": "string",
      "doc": "name of algorithm used to detect objects"
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
}"""