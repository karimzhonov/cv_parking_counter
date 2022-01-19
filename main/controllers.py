from main.views import *
from main.utils import handler

keys_handlers = [
    handler(keys=('--help',), render=help_render),
    handler(keys=('--run-detector',), render=run_detector),
    handler(keys=('--run-picker',), render=run_picker),
    handler(keys=('--run-detector', '--nonstop'), render=run_detector_nonstop, params={'nonstop': True})
]
