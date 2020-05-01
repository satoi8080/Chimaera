#!/usr/bin/env python

from config import *
from requests.exceptions import Timeout, ConnectionError
import time
import requests
import scrollphathd


def get_weather(condition_url=wttr_url):
    try:
        condition = requests.get(condition_url, timeout=5)
    except Timeout:
        report = [
            'Request Timeout, Check Network Connection.'
        ]
        print('Request Timeout, Check Network Connection.')
    except ConnectionError:
        report = [
            'Connection Error, Check Network Connection.'
        ]
        print('Connection Error, Check Network Connection.')
    else:
        current_condition = condition.json()['current_condition'][0]
        moon_phase = condition.json()['weather'][0]['astronomy'][0]['moon_phase']
        # https://en.wikipedia.org/wiki/Lunar_phase
        report = ['Condition: ' + current_condition['weatherDesc'][0]['value'],
                  'TEMP: ' + current_condition['temp_C'] + 'C',
                  'RH: ' + current_condition['humidity'] + '%',
                  'Moon: ' + moon_phase
                  ]
    return report


def scroll_once(content=None):
    scrollphathd.clear()
    if content is None:
        content = ["I could be bounded in a nutshell,",
                   "and count myself a king of infinite space.",
                   "--Hamlet: Act II, scene ii"
                   ]
    # Build the message
    lines = content

    # Determine how far apart each line should be spaced vertically
    line_height = scrollphathd.DISPLAY_HEIGHT + 2

    # Store the left offset for each subsequent line (starts at the end of the last line)
    offset_left = 0

    # Draw each line in lines to the Scroll pHAT HD buffer
    # scrollphathd.write_string returns the length of the written string in pixels
    # we can use this length to calculate the offset of the next line
    # and will also use it later for the scrolling effect.
    lengths = [0] * len(lines)

    for line, text in enumerate(lines):
        lengths[line] = scrollphathd.write_string(text, x=offset_left, y=line_height * line)
        offset_left += lengths[line]

    # This adds a little bit of horizontal/vertical padding into the buffer at
    # the very bottom right of the last line to keep things wrapping nicely.
    scrollphathd.set_pixel(offset_left - 1, (len(lines) * line_height) - 1, 0)

    # Reset the animation
    scrollphathd.scroll_to(0, 0)
    scrollphathd.show()

    # Keep track of the X and Y position for the rewind effect
    pos_x = 0
    pos_y = 0

    for current_line, line_length in enumerate(lengths):
        # Delay a slightly longer time at the start of each line
        time.sleep(delay * 10)

        # Scroll to the end of the current line
        for y in range(line_length):
            scrollphathd.scroll(1, 0)
            pos_x += 1
            time.sleep(delay)
            scrollphathd.show()

        # If we're currently on the very last line and rewind is True
        # We should rapidly scroll back to the first line.
        if current_line == len(lines) - 1 and rewind:
            for y in range(pos_y):
                scrollphathd.scroll(-int(pos_x / pos_y), -1)
                scrollphathd.show()
                time.sleep(delay)

        # Otherwise, progress to the next line by scrolling upwards
        else:
            for x in range(line_height):
                scrollphathd.scroll(0, 1)
                pos_y += 1
                scrollphathd.show()
                time.sleep(delay)


def infinite_scroll_weather():
    while True:
        content = get_weather(wttr_url)
        scroll_once(content)


if __name__ == '__main__':
    print("Press Ctrl-C to Escape")
    infinite_scroll_weather()
