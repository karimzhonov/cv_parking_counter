import cv2
import numpy as np

from main.utils import get_pos_list, set_pos_list, draw_place, put_text, is_end_video
from config import CAR_WIDTH, CAR_HEIGHT, FPS, PLACE_CHECKING_CONST


class SpacePicker:
    win_name = 'Image'

    def __init__(self, src, car_width=CAR_WIDTH, car_height=CAR_HEIGHT, params=None):
        self.src = src
        self.car_width = car_width
        self.car_height = car_height

    @staticmethod
    def draw_places_from_pickle(img):
        pos_list = get_pos_list()

        for x, y, in pos_list:
            img = draw_place(img, x, y, True)
        return img

    def mouse_click(self):
        def callback_func(event, x, y, flags, params):
            pos_list = get_pos_list()

            if event == cv2.EVENT_LBUTTONDOWN:
                pos_list.append((x, y))
            if event == cv2.EVENT_RBUTTONDOWN:
                for i, (x_pos, y_pos) in enumerate(pos_list):
                    if x_pos < x < x_pos + self.car_width and y_pos < y < y_pos + self.car_height:
                        pos_list.pop(i)

            set_pos_list(pos_list)

        cv2.setMouseCallback(self.win_name, callback_func)

    def imshow(self):
        video = cv2.VideoCapture(self.src)
        _, img = video.read()
        img = self.draw_places_from_pickle(img)
        cv2.imshow(self.win_name, img)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyWindow(self.win_name)
            return False
        return True

    def run(self):
        while self.imshow():
            self.mouse_click()


class Detector:
    win_name = 'Video'

    def __init__(self, cap_name, car_width=CAR_WIDTH, car_height=CAR_HEIGHT, params=None):
        self.cap_name = cap_name
        self.params = params
        self.car_width = car_width
        self.car_height = car_height

    @staticmethod
    def set_nonstop(cap: cv2.VideoCapture):
        if is_end_video(cap):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    @staticmethod
    def checking_space(img_place) -> tuple[bool, str]:
        count = cv2.countNonZero(img_place)
        return (True, str(count)) if count < PLACE_CHECKING_CONST else (False, str(count))

    def imshow(self, img):
        cv2.imshow(self.win_name, img)
        return not cv2.waitKey(int(1000/FPS)) == ord('q')

    def render(self, img):
        counter_empty_place = 0
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(img_blur, 255,
                                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY_INV, 25, 16)
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)

        pos_list = get_pos_list()
        for x, y, in pos_list:
            place = img_dilate[y: y + self.car_height, x: x + self.car_width]
            isempty, text = self.checking_space(place)
            counter_empty_place += 1 if isempty else 0
            img = draw_place(img, x, y, isempty)
            put_text(img, x, y, text, scale=1, isempty=isempty)
        put_text(img, 48, 0, f'Empty places: {counter_empty_place}, All places: {len(pos_list)}', scale=2, isempty=True)
        return img

    def run(self):
        video = cv2.VideoCapture(self.cap_name)
        while True:
            try:
                if self.params['nonstop']:
                    self.set_nonstop(video)
            except TypeError:
                if is_end_video(video):
                    break

            _, img = video.read()

            img = self.render(img)
            if not self.imshow(img):
                break
        cv2.destroyAllWindows()
        video.release()
