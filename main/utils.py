import pickle
import cv2

from config import POS_LIST_PATH, EMPTY_COLOR, NO_EMPTY_COLOR, CAR_WIDTH, CAR_HEIGHT


def arg_max(array:list):
    m = array[0]
    i = 0
    for j, point in enumerate(array):
        if m < point:
            m = point
            i = j
    return i


def get_pathname_from_args(flags):
    try:
        return flags[1]
    except IndexError:
        return 0


def get_pos_list():
    with open(POS_LIST_PATH, 'rb') as file:
        return pickle.load(file)


def set_pos_list(pos_list):
    with open(POS_LIST_PATH, 'wb') as file:
        pickle.dump(pos_list, file)


def draw_place(img,  left: int, top: int, isempty: bool):
    color = EMPTY_COLOR if isempty else NO_EMPTY_COLOR
    return cv2.rectangle(img, (left, top), (left + CAR_WIDTH, top + CAR_HEIGHT), color, 3)


def put_text(img, x, y, text, scale, isempty):
    import cvzone
    cvzone.putTextRect(img,
                       text=text,
                       pos=(x, y + CAR_HEIGHT - 3),
                       scale=scale, thickness=2, offset=0,
                       colorR=EMPTY_COLOR if isempty else NO_EMPTY_COLOR)


def run(sys_args):
    from main.controllers import keys_handlers

    def start_handlers(handlers, _flags):
        responses = []
        for keys, render, params in handlers:
            counter = 0
            for key in keys:
                if key in _flags:
                    counter += 1
            responses.append(counter)

        max_arg = arg_max(responses)
        _, render, params = handlers[max_arg]
        render(_flags, params)

    if len(sys_args) == 1:
        from main.views import help_render
        help_render(sys_args[1:])
    else:
        start_handlers(keys_handlers, sys_args[1:])


def is_end_video(cap: cv2.VideoCapture):
    return cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT)


def handler(keys: tuple, render, params=None):
    return keys, render, params
