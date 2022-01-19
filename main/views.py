from main.models import Detector, SpacePicker
from main.utils import get_pathname_from_args


def help_render(flags: list, params=None):
    """
    manage.py --help: For more information
    """
    from main.controllers import keys_handlers
    print('About script')
    for _, render, _ in keys_handlers:
        print(render.__doc__)


def run_detector(flags: list, params=None):
    """
    manage.py --run-detector <video_path or capture_path>: This command run script for detection one time
    """
    src = get_pathname_from_args(flags)
    print('For quit press "q"')
    Detector(src, params=params).run()


def run_detector_nonstop(flags, params=None):
    """
    manage.py --run-detector <video_path or capture_path> --nonstop: This command run script for detection nore time
    """
    src = get_pathname_from_args(flags)
    print('For quit press "q"')
    Detector(src, params=params).run()


def run_picker(flags: list, params=None):
    """
    manage.py --run-picker <video_path or capture_path>: This command run script for picking empty place first frame in video
    """
    src = get_pathname_from_args(flags)
    print('For quit press "q"')
    SpacePicker(src, params=params).run()

