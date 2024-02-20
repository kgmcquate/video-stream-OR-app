from .detectors import YOLOv3Detector #, FasterRCNNMobileNetDetector, FasterRCNNResNetDetector
from .records import RawImageRecord
import cv2
import numpy as np

def main():


    filename = "app/04union-square-lqmb-superJumbo.jpg" #"app/cat.jpg" #"app/04union-square-lqmb-superJumbo.jpg" # "app/n01443537_goldfish.JPEG" # 
    with open(filename, "rb") as f:
        jpeg_image = f.read()

    # raw_image = RawImageRecord("test", "test", "test", "test", jpeg_image, "{}")

    # processed_images = raw_image.process_image()


    # detector = FasterRCNNMobileNetDetector() #
    detector = YOLOv3Detector()
    # detector = FasterRCNNResNetDetector()

    image = cv2.imdecode(
                np.frombuffer(jpeg_image, np.uint8),
                cv2.IMREAD_COLOR
            )

    processed_images = detector.process(
        image,
        **{
            'source_name': "asd", 
            'video_stream_id': "asd", 
            'frame_ts': "asd", 
            'id': "asd", 
            'metadata': "asd"
        }
    )

    print(processed_images)