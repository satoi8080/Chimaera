import scrollphathd
from datetime import datetime, timedelta, timezone

# Only JSON format is supported in this program, read https://github.com/chubin/wttr.in#json-output
wttr_url = "https://wttr.in/Tokyo?format=j1"
# Timezone setup
local_time = timezone(timedelta(hours=+9))


# Uncomment the below if your display is upside down
#   (e.g. if you're using it in a Pimoroni Scroll Bot)
scrollphathd.rotate(degrees=180)

# Dial down the brightness
scrollphathd.set_brightness(0.1)

# If rewind is True the scroll effect will rapidly rewind after the last line
rewind = False

# Delay is the time (in seconds) between each pixel scrolled
delay = 0.01
