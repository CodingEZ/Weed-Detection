import cv2
import numpy
import math
from enum import Enum

class GripPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """
    
    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__hsv_threshold_hue = [45.323743322770376, 180.0]
        self.__hsv_threshold_saturation = [0.0, 170.8702961007076]
        self.__hsv_threshold_value = [0.0, 247.74743473977358]

        self.hsv_threshold_output = None

        self.__find_contours_input = self.hsv_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 0.0
        self.__filter_contours_min_perimeter = 0
        self.__filter_contours_min_width = 0
        self.__filter_contours_max_width = 1000.0
        self.__filter_contours_min_height = 0
        self.__filter_contours_max_height = 1000
        self.__filter_contours_solidity = [0.0, 100.0]
        self.__filter_contours_max_vertices = 1000000
        self.__filter_contours_min_vertices = 100.0
        self.__filter_contours_min_ratio = 0
        self.__filter_contours_max_ratio = 1000

        self.filter_contours_output = None

        self.__distance_transform_input = self.hsv_threshold_output
        self.__distance_transform_type = cv2.DIST_L1
        self.__distance_transform_mask_size = 0

        self.distance_transform_output = None

        self.__normalize_input = self.distance_transform_output
        self.__normalize_type = cv2.NORM_MINMAX
        self.__normalize_alpha = 0.0
        self.__normalize_beta = 255.0

        self.normalize_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSV_Threshold0:
        self.__hsv_threshold_input = source0
        (self.hsv_threshold_output) = self.__hsv_threshold(self.__hsv_threshold_input, self.__hsv_threshold_hue, self.__hsv_threshold_saturation, self.__hsv_threshold_value)

        # Step Find_Contours0:
        self.__find_contours_input = self.hsv_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input, self.__find_contours_external_only)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours, self.__filter_contours_min_area, self.__filter_contours_min_perimeter, self.__filter_contours_min_width, self.__filter_contours_max_width, self.__filter_contours_min_height, self.__filter_contours_max_height, self.__filter_contours_solidity, self.__filter_contours_max_vertices, self.__filter_contours_min_vertices, self.__filter_contours_min_ratio, self.__filter_contours_max_ratio)

        # Step Distance_Transform0:
        self.__distance_transform_input = self.hsv_threshold_output
        (self.distance_transform_output) = self.__distance_transform(self.__distance_transform_input, self.__distance_transform_type, self.__distance_transform_mask_size)

        # Step Normalize0:
        self.__normalize_input = self.distance_transform_output
        (self.normalize_output) = self.__normalize(self.__normalize_input, self.__normalize_type, self.__normalize_alpha, self.__normalize_beta)

    @staticmethod
    def __hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy =cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            '''
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            '''
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

    @staticmethod
    def __distance_transform(input, type, mask_size):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.array.
            type: Opencv enum.
            mask_size: The size of the mask. Either 0, 3, or 5.
        Returns:
            A black and white numpy.ndarray.
        """
        h, w = input.shape[:2]
        dst = numpy.zeros((h, w), numpy.float32)
        cv2.distanceTransform(input, type, mask_size, dst = dst)
        return numpy.uint8(dst)

    @staticmethod
    def __normalize(input, type, a, b):
        """Normalizes or remaps the values of pixels in an image.
        Args:
            input: A numpy.ndarray.
            type: Opencv enum.
            a: The minimum value.
            b: The maximum value.
        Returns:
            A numpy.ndarray of the same type as the input.
        """
        return cv2.normalize(input, None, a, b, type)


def please(img):
    processClass = GripPipeline()
    #img = cv2.imread('TestLeaves.jpg', 1)
    processClass.process(img)
    return processClass.normalize_output
