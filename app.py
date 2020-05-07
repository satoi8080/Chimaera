from flask import Flask, render_template, url_for
import scrollphathd
from requests.exceptions import Timeout, ConnectionError
import time
import requests
import threading
import os
import datetime


# --------------------------------------------------

# Only JSON format is supported in this program,
# read https://github.com/chubin/wttr.in#json-output
WTTR_URL = "https://wttr.in/Chiyoda?format=j1"

# Timezone setup
LOCAL_TIME_ZONE = datetime.timezone(datetime.timedelta(hours=+9))

# Display setup
scrollphathd.rotate(degrees=180)
scrollphathd.set_clear_on_exit()
scrollphathd.set_brightness(0.1)
scrollphathd.clear()

REWIND = False
global LOOP
LOOP = True
DELAY = 0.01


# --------------------------------------------------

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_weather', methods=['POST'])
def start_weather():
    global LOOP
    LOOP = True
    scrollphathd.clear()
    weather_circulation_thread = threading.Thread(target=weather_circulation(), name='Weather Circulation')
    weather_circulation_thread.start()
    return '0'


@app.route('/clear', methods=['POST'])
def clear():
    global LOOP
    LOOP = False
    scrollphathd.clear()
    return '0'


def weather(condition_url=WTTR_URL):
    try:
        condition = requests.get(condition_url, timeout=5)
    except Timeout:
        report = [
            'Request Timeout,',
            'Check Network.'
        ]
        print('Request Timeout, Check Network.')
        os.system('sudo /etc/init.d/networking restart')
    except ConnectionError:
        report = [
            'Connection Error,',
            'Check Network.'
        ]
        print('Connection Error, Check Network.')
        os.system('sudo /etc/init.d/networking restart')
    else:
        current_condition = condition.json()['current_condition'][0]
        moon_phase = condition.json()['weather'][0]['astronomy'][0]['moon_phase']
        # https://en.wikipedia.org/wiki/Lunar_phase
        report = [datetime.datetime.now(LOCAL_TIME_ZONE).ctime(),
                  'Condition: ' + current_condition['weatherDesc'][0]['value'],
                  'T: ' + current_condition['temp_C'] + 'C',
                  'RH: ' + current_condition['humidity'] + '%',
                  'Moon: ' + moon_phase
                  ]
    return report


def scroll(content=None):
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
        time.sleep(DELAY * 10)

        # Scroll to the end of the current line
        for y in range(line_length):
            scrollphathd.scroll(1, 0)
            pos_x += 1
            time.sleep(DELAY)
            scrollphathd.show()

        # If we're currently on the very last line and rewind is True
        # We should rapidly scroll back to the first line.
        if current_line == len(lines) - 1 and REWIND:
            for y in range(pos_y):
                scrollphathd.scroll(-int(pos_x / pos_y), -1)
                scrollphathd.show()
                time.sleep(DELAY)

        # Otherwise, progress to the next line by scrolling upwards
        else:
            for x in range(line_height):
                scrollphathd.scroll(0, 1)
                pos_y += 1
                scrollphathd.show()
                time.sleep(DELAY)


def weather_circulation():
    while True:
        content = weather(WTTR_URL)
        scroll(content)
        global LOOP
        if not LOOP:
            break


@app.route('/poweroff', methods=['Post'])
def poweroff():
    scrollphathd.clear()
    os.system("sudo poweroff")
    return '0'


@app.route('/reboot', methods=['Post'])
def reboot():
    scrollphathd.clear()
    os.system("sudo reboot")
    return '0'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
