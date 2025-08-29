import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from datetime import datetime

DB_FILE = "tags.sqlite"
O2_TAG_ID = 705
CO_TAG_ID = 398
N_POINTS = 50

def parse_datetime(timestr):
    # Attempt multiple formats
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",  # with microseconds
        "%Y-%m-%d %H:%M:%S"      # without microseconds
    ]
    for fmt in formats:
        try:
            return datetime.strptime(timestr, fmt)
        except ValueError:
            pass
    raise ValueError(f"Time data '{timestr}' does not match any known formats.")

def get_tag_data(tag_id, conn, limit=50):
    query = """
    SELECT Value, DateTime
    FROM TagValues
    WHERE TagName_id = ?
      AND date(DateTime) = date('now')
    ORDER BY DateTime DESC
    LIMIT ?
    """
    cur = conn.cursor()
    cur.execute(query, (tag_id, limit))
    rows = cur.fetchall()
    rows.reverse()  # Reverse since fetched in descending order

    values = []
    times = []
    for val, timestr in rows:
        values.append(float(val))
        dt_obj = parse_datetime(timestr)
        times.append(dt_obj)

    return times, values

conn = sqlite3.connect(DB_FILE)

fig, ax = plt.subplots(figsize=(10, 5))
ax2 = ax.twinx()  # Create a secondary y-axis sharing the same x-axis

ax.set_title("Real-Time O2 and CO Concentration (Today)")
ax.set_xlabel("Time")
ax.set_ylabel("O2 (%)")
ax2.set_ylabel("CO (PPM)")

# Plot lines initially empty
o2_line, = ax.plot([], [], label="O2 (%)", color='tab:blue')
co_line, = ax2.plot([], [], label="CO (PPM)", color='tab:red')

# Format x-axis for time
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

# We will manage legends manually to show both lines
lines = [o2_line, co_line]
ax.legend(lines, [l.get_label() for l in lines], loc="upper left")

def update(frame):
    # Fetch data for O2 and CO
    o2_times, o2_values = get_tag_data(O2_TAG_ID, conn, N_POINTS)
    co_times, co_values = get_tag_data(CO_TAG_ID, conn, N_POINTS)

    # Update O2 line (left axis)
    o2_line.set_data(o2_times, o2_values)
    # Update CO line (right axis)
    co_line.set_data(co_times, co_values)

    # Adjust x-axis if we have data
    all_times = o2_times + co_times
    if all_times:
        xmin, xmax = min(all_times), max(all_times)
        ax.set_xlim(xmin, xmax)

    # Adjust y-axis for O2 if we have O2 data
    if o2_values:
        ymin_o2, ymax_o2 = min(o2_values), max(o2_values)
        margin_o2 = (ymax_o2 - ymin_o2) * 0.1 if ymax_o2 != ymin_o2 else 1
        ax.set_ylim(ymin_o2 - margin_o2, ymax_o2 + margin_o2)

    # Adjust y-axis for CO if we have CO data
    if co_values:
        ymin_co, ymax_co = min(co_values), max(co_values)
        margin_co = (ymax_co - ymin_co)*0.1 if ymax_co != ymin_co else 1
        ax2.set_ylim(ymin_co - margin_co, ymax_co + margin_co)

    return o2_line, co_line

ani = FuncAnimation(fig, update, interval=2000, blit=False, cache_frame_data=False)
plt.tight_layout()
plt.show()

conn.close()
