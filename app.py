from flask import Flask, render_template
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
DELAY = 0.01

# --------------------------------------------------

app = Flask(__name__)


class WeatherController:
    def __init__(self):
        self.loop = False
        self.thread = None

    def start(self):
        """Start the weather display loop in a new thread."""
        if not self.loop:  # Avoid starting multiple threads
            self.loop = True
            scrollphathd.clear()
            scrollphathd.show()
            self.thread = threading.Thread(target=self.weather_circulation, name='Weather Circulation')
            self.thread.start()

    def stop(self):
        """Stop the weather display loop."""
        self.loop = False
        scrollphathd.clear()
        scrollphathd.show()

    def weather(self, condition_url=WTTR_URL):
        try:
            response = requests.get(condition_url, timeout=5)
            response.raise_for_status()  # Check for HTTP errors
        except Timeout:
            report = [
                'Request Timeout,',
                'Check Network.'
            ]
            print('Request Timeout, Check Network.')
        except ConnectionError:
            report = [
                'Connection Error,',
                'Check Network.'
            ]
            print('Connection Error, Check Network.')
        except requests.RequestException as e:
            report = [
                'Error occurred:',
                str(e)
            ]
            print(f'Error occurred: {e}')
        else:
            try:
                current_condition = response.json()['current_condition'][0]
                moon_phase = response.json()['weather'][0]['astronomy'][0]['moon_phase']
                report = [
                    datetime.datetime.now(LOCAL_TIME_ZONE).ctime(),
                    'Condition: ' + current_condition['weatherDesc'][0]['value'],
                    'T: ' + current_condition['temp_C'] + 'C',
                    'RH: ' + current_condition['humidity'] + '%',
                    'Moon: ' + moon_phase
                ]
            except (KeyError, IndexError):
                report = ['Error: Invalid data from weather service.']
                print('Error: Invalid data structure in response.')
        return report

    def scroll(self, content=None):
        scrollphathd.clear()
        if content is None:
            content = ["I could be bounded in a nutshell,",
                       "and count myself a king of infinite space.",
                       "--Hamlet: Act II, scene ii"
                       ]

        # Determine how far apart each line should be spaced vertically
        line_height = scrollphathd.DISPLAY_HEIGHT + 2

        # Store the left offset for each subsequent line (starts at the end of the last line)
        offset_left = 0

        # Draw each line in lines to the Scroll pHAT HD buffer
        lengths = [scrollphathd.write_string(text, x=offset_left, y=line_height * i) for i, text in enumerate(content)]
        offset_left += sum(lengths)

        # This adds a little bit of padding at the bottom right
        scrollphathd.set_pixel(offset_left - 1, (len(content) * line_height) - 1, 0)

        # Reset the animation
        scrollphathd.scroll_to(0, 0)
        scrollphathd.show()

        # Track the current position
        pos_x = 0
        pos_y = 0

        for current_line, line_length in enumerate(lengths):
            # Delay a slightly longer time at the start of each line
            time.sleep(DELAY * 10)

            # Scroll to the end of the current line
            for _ in range(line_length):
                scrollphathd.scroll(1, 0)
                pos_x += 1
                time.sleep(DELAY)
                scrollphathd.show()

                if not self.loop:
                    return  # Exit scrolling if loop is stopped

            # If we're on the last line and REWIND is enabled, scroll back up
            if current_line == len(lengths) - 1 and REWIND:
                for _ in range(pos_y):
                    scrollphathd.scroll(-int(pos_x / pos_y), -1)
                    scrollphathd.show()
                    time.sleep(DELAY)
            else:
                for _ in range(line_height):
                    scrollphathd.scroll(0, 1)
                    pos_y += 1
                    scrollphathd.show()
                    time.sleep(DELAY)

    def weather_circulation(self):
        """Loop to continuously fetch and display weather information."""
        while self.loop:
            content = self.weather(WTTR_URL)
            self.scroll(content)
            if not self.loop:
                break


# Initialize the weather controller
weather_controller = WeatherController()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_weather', methods=['POST'])
def start_weather():
    weather_controller.start()
    return '0'


@app.route('/clear', methods=['POST'])
def clear():
    weather_controller.stop()
    return '0'


@app.route('/poweroff', methods=['POST'])
def poweroff():
    scrollphathd.clear()
    os.system("sudo poweroff")
    return '0'


@app.route('/reboot', methods=['POST'])
def reboot():
    scrollphathd.clear()
    os.system("sudo reboot")
    return '0'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)