import cv2
import dataclasses
from typing import Dict, List, Tuple, Any
import numpy as np
import os
import boto3
import logging
from .common import BaseObjectDetector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

model_files_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_files")


@dataclasses.dataclass
class YOLOv3Detector(BaseObjectDetector):
    bounding_box_color: Tuple[int, int, int] = (255, 0, 0)
    detector_name: str = "yolo_v3"
    detector_version: str = "0.0.3"

    def __post_init__(self):

        self.weights_file = "yolov3.weights" #os.path.join(model_files_path, )

        with open(os.path.join(model_files_path, "coco.names"), "r") as f:
            self.classes = [line.strip() for line in f]

        # self.layer_names = self.net.getUnconnectedOutLayersNames()

        self.confidence_limit = 0.80


    def process(self, image: np.array, **kwargs) -> List["ProcessedImage"]:
        """Returns processed image and metadata dict"""
        from ..records import ProcessedImage

        if not os.path.exists(self.weights_file):
            logger.warn("Downloading yolov3 weights")
            s3_client = boto3.client('s3')
            s3_client.download_file('deployment-zone-117819748843', 'image-classifier/yolov3.weights', self.weights_file)
            # resp = requests.get("https://pjreddie.com/media/files/yolov3.weights")
            # resp.raise_for_status()
            # with open(self.weights_file, "wb") as f:
            #     f.write(resp.content)
            logger.warn("Completed downloading yolov3 weights")

        net = cv2.dnn.readNet(
            self.weights_file, 
            os.path.join(model_files_path, "yolov3.cfg")
        )

        layer_names = net.getUnconnectedOutLayersNames()

        # load image
        height, width, _ = image.shape

        # Preprocess image for YOLO
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)

        # Run forward pass
        outs = net.forward(layer_names)

        # Get bounding boxes, confidence scores, and class IDs
        boxes = []
        confidences = []
        class_ids = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.confidence_limit:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append((x, y, w, h))
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-maximum suppression to remove overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        filtered_boxes = [(boxes[i], self.classes[class_ids[i]] ) for i in indices]

        object_names = {object_name for _, object_name in filtered_boxes}

        processed_images = []
        for object_name in object_names:
            object_boxes = [box for box, obj_name in filtered_boxes if object_name == obj_name ]
            processed_images.append(
                ProcessedImage(
                    image=image,
                    object_name=object_name,
                    object_bounding_boxes=[(int(x), int(y), int(w), int(h)) for (x, y, w, h) in object_boxes], 
                    detector_name=self.detector_name,
                    detector_version=self.detector_version,
                    **kwargs
                )
            )
            
        return processed_images
    