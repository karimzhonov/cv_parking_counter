import cv2
import numpy as np

from main.utils import get_pos_list, set_pos_list, draw_place, put_text, is_end_video
from config import FPS, PLACE_CHECKING_CONST


class SpacePicker:
    win_name = 'Image'
    x1_y1 = None
    # pos_list = []

    def __init__(self, src, params=None):
        self.src = src
        self.params = params

    @staticmethod
    def draw_places_from_pickle(img):
        pos_list = get_pos_list()
        # pos_list = self.pos_list

        for (x1, y1,), (x2, y2) in pos_list:
            img = draw_place(img, (x1, y1), (x2, y2), True)
        return img

    def mouse_click(self):
        def callback_func(event, x, y, flags, params):
            pos_list = get_pos_list()
            # pos_list = self.pos_list

            if event == cv2.EVENT_LBUTTONDOWN:
                self.x1_y1 = (x, y)
                # pos_list.append((x, y))
            if event == cv2.EVENT_LBUTTONUP:
                pos_list.append((self.x1_y1, (x, y)))
            if event == cv2.EVENT_RBUTTONDOWN:
                for i, ((x1, y1), (x2, y2)) in enumerate(pos_list):
                    if x1 < x < x2 and y1 < y < y2:
                        pos_list.pop(i)

            set_pos_list(pos_list)

        cv2.setMouseCallback(self.win_name, callback_func,)

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
        print('[INFO] For pick space parking: mouse down and move mouse then mouse up')
        while self.imshow():
            self.mouse_click()


class Detector:
    win_name = 'Video'

    def __init__(self, cap_name, params=None):
        self.cap_name = cap_name
        self.params = params

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
        for (x1, y1), (x2, y2) in pos_list:
            place = img_dilate[y1: y2, x1: x2]
            isempty, text = self.checking_space(place)
            counter_empty_place += 1 if isempty else 0
            img = draw_place(img, (x1, y1), (x2, y2), isempty)
            put_text(img, x1, y1, text, scale=1, isempty=isempty)
        put_text(img, 40, 40, f'Empty places: {counter_empty_place}, All places: {len(pos_list)}', scale=2, isempty=True)
        return img

    def run(self):
        video = cv2.VideoCapture(self.cap_name)
        _, img = video.read()
        while self.imshow(img):
            try:
                if self.params['nonstop']:
                    self.set_nonstop(video)
            except TypeError:
                if is_end_video(video):
                    break

            _, img = video.read()

            img = self.render(img)
        cv2.destroyAllWindows()
        video.release()
