import cv2
import dataclasses
from typing import Dict, List, Tuple, Any
import numpy as np
import copy
import os
import requests
import boto3
import logging

from .common import BaseObjectDetector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)





@dataclasses.dataclass
class HAARClassifier(BaseObjectDetector):
    bounding_box_color: Tuple[int, int, int] = (255, 0, 0)
    detector_name: str = "haar_classifier"
    detector_version: str = "0.0.1"
    target_object_name: str = "person"
    haar_cascade_file: str = cv2.data.haarcascades + "haarcascade_fullbody.xml"

    # class
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def __post_init__(self):
        self.cv2_classifier = cv2.CascadeClassifier(self.haar_cascade_file)

    def process(self, image: np.array, **kwargs) -> "ProcessedImage":
        """Returns processed image and metadata dict"""
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Getting corners around the face
        # 1.3 = scale factor, 5 = minimum neighbor can be detected
        objs = self.cv2_classifier.detectMultiScale(img_gray, 1.05, 3)  

        # drawing bounding box around face
        for (x, y, w, h) in objs:
            image = cv2.rectangle(image, (x, y), (x + w, y + h), self.bounding_box_color, 3)

        # displaying image with bounding box
        # cv2.imshow('face_detect', img)
        
        from ..records import ProcessedImage
        return [ProcessedImage(
                        image=image,
                        object_name=self.target_object_name,
                        object_bounding_boxes=[(int(x), int(y), int(w), int(h)) for (x, y, w, h) in objs], 
                        detector_name=self.detector_name,
                        detector_version=self.detector_version,
                        **kwargs
                    )]
    



# @dataclasses.dataclass
# class ResNetDetector(BaseObjectDetector):
#     bounding_box_color: Tuple[int, int, int] = (255, 0, 0)
#     detector_name: str = "haar_classifier"
#     detector_version: str = "0.0.1"
#     target_object_name: str = "person"

#     def __post_init__(self):
#         self.cv2_classifier = cv2.CascadeClassifier(self.haar_cascade_file)

#     def process(self, image: np.array, **kwargs) -> "ProcessedImage":
#         """Returns processed image and metadata dict"""
#         img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#         # Getting corners around the face
#         # 1.3 = scale factor, 5 = minimum neighbor can be detected
#         objs = self.cv2_classifier.detectMultiScale(img_gray, 1.05, 3)  

#         # drawing bounding box around face
#         for (x, y, w, h) in objs:
#             image = cv2.rectangle(image, (x, y), (x + w, y + h), self.bounding_box_color, 3)

#         # displaying image with bounding box
#         # cv2.imshow('face_detect', img)
        
#         from .records import ProcessedImage
#         return ProcessedImage(
#                         image=image,
#                         object_name=self.target_object_name,
#                         object_bounding_boxes=[(int(x), int(y), int(w), int(h)) for (x, y, w, h) in objs], 
#                         detector_name=self.detector_name,
#                         detector_version=self.detector_version,
#                         **kwargs
#                     )
    


 #, ResNetDetector()]

