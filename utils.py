import time
from init import g


def sync_time():
    if g['redis'].exists('curr_week'):
        curr_week = int(g['redis'].get('curr_week'))
    else:
        curr_week = 1543996800
    while curr_week + 604800 < time.time():
        curr_week = curr_week + 604800
    g['redis'].set('curr_week', curr_week)
    g['redis'].set('next_week', curr_week + 604800)
