import sys
import subprocess
import sqlite3
from datetime import datetime
import csv
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import ScalarFormatter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QPainter, QColor, QBrush, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
DB_FILE   = "tags.sqlite"
O2_TAG_ID = 705
CO_TAG_ID = 398
MAX_POINTS = 500            # final scrolling window
START_POINTS = 50           # what we show on start


# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------
def parse_datetime(timestr: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(timestr, fmt)
        except ValueError:
            pass
    raise ValueError(f"Bad datetime: {timestr}")


def get_tag_data(tag_id: int, connection, limit: int):
    cur = connection.cursor()
    cur.execute(
        """
        SELECT Value, DateTime
        FROM TagValues
        WHERE TagName_id = ?
        ORDER BY DateTime DESC
        LIMIT ?
        """,
        (tag_id, limit),
    )
    rows = cur.fetchall()
    rows.reverse()                                     # chronological
    times, values = [], []
    for val, t in rows:
        try:
            values.append(float(val))
            times.append(parse_datetime(t))
        except (ValueError, TypeError):
            continue
    return times, values


# ------------------------------------------------------------------
# small round “LED” widget
# ------------------------------------------------------------------
class LampIndicator(QWidget):
    def __init__(self, color=QColor("red"), diameter=16, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._d = diameter
        self.setFixedSize(diameter, diameter)

    def setColor(self, color):
        self._color = QColor(color)
        self.update()

    # draw
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        glow = QColor(self._color)
        glow.setAlpha(80)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(0, 0, self._d, self._d)
        p.setBrush(QBrush(self._color))
        margin = self._d // 6
        p.drawEllipse(margin, margin, self._d - 2 * margin, self._d - 2 * margin)


# ------------------------------------------------------------------
# main window
# ------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CO & O2 Analyser")

        # state flags
        self.process = None
        self.connected = False

        # timers
        self.status_timer = None
        self.measurement_timer = None

        # measurement stuff
        self.measurement_start_time = None
        self.measurement_line = None
        self.measurement_number = 1

        # plotting parameters
        self.display_points = START_POINTS   # grows to MAX_POINTS

        self._build_ui()
        self._build_menu()
        self._build_animation()

    # ------------- UI -------------------------------------------------------
    def _build_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)

        # ------------------------------------------------ buttons + lamps
        top = QHBoxLayout()
        self.connection_indicator = LampIndicator(QColor("red"))
        self.connect_button = QPushButton("Connect")
        self.start_button   = QPushButton("Start")
        self.abort_button   = QPushButton("Abort")

        top.addWidget(self.connection_indicator)
        top.addWidget(self.connect_button)
        top.addWidget(self.start_button)
        top.addWidget(self.abort_button)
        layout.addLayout(top)

        self.connect_button.clicked.connect(self.on_connect)
        self.start_button.clicked.connect(self.on_start)
        self.abort_button.clicked.connect(self.on_abort)

        # ------------------------------------------------ live value labels
        live = QHBoxLayout()
        self.o2_value_label = QLabel("O₂: -- %")
        self.co_value_label = QLabel("CO: -- ppm")
        big = QFont("Arial", 20, QFont.Weight.Bold)     
        self.o2_value_label.setFont(big)
        self.co_value_label.setFont(big)

        live.addStretch(1)
        live.addWidget(self.o2_value_label)
        live.addWidget(self.co_value_label)
        live.addStretch(1)
        layout.addLayout(live)

        # ------------------------------------------------ figure
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ax2 = self.ax.twinx()

        self.ax.set_title("Real-Time O₂ / CO concentrations")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("O₂ (%)", color="tab:blue")
        self.ax.tick_params(axis="y", labelcolor="tab:blue")
        self.fig.subplots_adjust(right=0.86)

        self.ax2.set_ylabel("CO (ppm)", color="tab:red")
        self.ax2.tick_params(axis="y", labelcolor="tab:red")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        # stop scientific / offset notation on both y axes
        plain = ScalarFormatter(useOffset=False)
        plain.set_scientific(False)

        self.ax.yaxis.set_major_formatter(plain)   # O₂ axis
        self.ax2.yaxis.set_major_formatter(plain)  # CO axis (optional)

        self.o2_line, = self.ax.plot([], [], label="O₂ (%)",  color="tab:blue")
        self.co_line, = self.ax2.plot([], [], label="CO (ppm)", color="tab:red")
        self.ax.legend(loc="upper left")

        canvas = FigureCanvas(self.fig)
        layout.addWidget(canvas)
        self.canvas = canvas


    # ------------- menu -----------------------------------------------------
    def _build_menu(self):
        bar = self.menuBar()
        # --- File
        file_menu = bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # --- Help
        help_menu = bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(
            lambda: QMessageBox.about(self, "About", "CO & O₂ Analyser GUI")
        )
        help_menu.addAction(about_action)


    # ------------- animation ------------------------------------------------
    def _build_animation(self):
        self.ani = FuncAnimation(
            self.fig, self.update_graph,
            interval=2000, blit=False, cache_frame_data=False
        )

    # ------------------------------------------------------------------------
    # data / plot update
    # ------------------------------------------------------------------------
    def update_graph(self, _frame):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                # grow window until it reaches MAX_POINTS
                if self.connected and self.display_points < MAX_POINTS:
                    self.display_points += 1

                o2_t, o2_v = get_tag_data(O2_TAG_ID, conn, self.display_points)
                co_t, co_v = get_tag_data(CO_TAG_ID, conn, self.display_points)

                if not (o2_t and co_t):
                    return self.o2_line, self.co_line

                # update lines
                self.o2_line.set_data(o2_t, o2_v)
                self.co_line.set_data(co_t, co_v)

                # live labels (latest value == last in list)
                self.o2_value_label.setText(f"O₂: {o2_v[-1]:.2f} %")
                self.co_value_label.setText(f"CO: {co_v[-1]:.0f} ppm")

                # x-axis
                all_times = o2_t + co_t
                self.ax.set_xlim(min(all_times), max(all_times))

                # y-axis O2
                y_min, y_max = min(o2_v), max(o2_v)
                pad = (y_max - y_min) * 0.1 or 1
                self.ax.set_ylim(y_min - pad, y_max + pad)

                # y-axis CO
                y2_min, y2_max = min(co_v), max(co_v)
                pad2 = (y2_max - y2_min) * 0.1 or 1
                self.ax2.set_ylim(y2_min - pad2, y2_max + pad2)

                self.canvas.draw_idle()
        except sqlite3.Error as e:
            print("DB error:", e)

        return self.o2_line, self.co_line


    # ------------------------------------------------------------------------
    # connect / disconnect handling
    # ------------------------------------------------------------------------
    def on_connect(self):
        # toggle
        if self.connected:
            self.on_disconnect()
            return

        try:
            # launch analyser script
            self.process = subprocess.Popen([sys.executable, "CO_O2Analyser.py"])  # "instr_simulator.py"
            # poll status file every second
            self.status_timer = QTimer(self)
            self.status_timer.timeout.connect(self.check_connection_status)
            self.status_timer.start(1000)
        except Exception as e:
            print("Cannot launch analyser:", e)

    def on_disconnect(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
        self.process = None
        if self.status_timer:
            self.status_timer.stop()
            self.status_timer = None

        self.connected = False
        self.display_points = START_POINTS      # shrink plot again
        self.connect_button.setText("Connect")
        self.connection_indicator.setColor("red")

    def check_connection_status(self):
        try:
            with open("analyser_status.txt", "r") as f:
                status = (f.readlines()[-1].strip() or "").upper()
        except Exception:
            status = ""

        if status == "CONNECTED":
            self.connection_indicator.setColor("green")
            self.connect_button.setText("Disconnect")
            self.connected = True
            # status checks can be slower now
            self.status_timer.setInterval(10_000)
        else:
            self.on_disconnect()


    # ------------------------------------------------------------------------
    # measurement start / stop / abort
    # ------------------------------------------------------------------------
    def on_start(self):
        if not self.ani.event_source:
            print("Animation source missing")
            return

        # resume animation
        self.ani.event_source.start()

        self.measurement_start_time = datetime.now()
        if self.measurement_line:
            self.measurement_line.remove()
        self.measurement_line = self.ax.axvline(
            x=self.measurement_start_time, color="blue",
            linestyle="--", label="Start"
        )

        # one-shot timer (minutes → ms)
        if self.measurement_timer is None:
            self.measurement_timer = QTimer(self)
            self.measurement_timer.timeout.connect(self.stop_measurement)
        self.measurement_timer.start(15 * 60 * 1000)

        self.start_button.setEnabled(False)
        self.canvas.draw_idle()

    def stop_measurement(self):
        if self.measurement_timer:
            self.measurement_timer.stop()

        end_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"M{self.measurement_number}_END{end_ts}.csv"

        with sqlite3.connect(DB_FILE) as conn, open(fname, "w", newline="") as f:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT O2.DateTime, O2.Value, CO.Value
                FROM TagValues O2
                JOIN TagValues CO ON O2.DateTime = CO.DateTime
                WHERE O2.TagName_id = {O2_TAG_ID}
                  AND CO.TagName_id = {CO_TAG_ID}
                  AND O2.DateTime BETWEEN ? AND ?
                ORDER BY O2.DateTime DESC
                """,
                (
                    self.measurement_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            rows = cur.fetchall()
            csv.writer(f).writerows([("DateTime", "O2_CONC", "CO_CONC"), *rows])

        self.measurement_number += 1
        self.start_button.setEnabled(True)
        if self.measurement_line:
            self.measurement_line.remove()
            self.measurement_line = None
        self.canvas.draw_idle()

        QMessageBox.information(self, "Done", f"Saved to {fname}")

    def on_abort(self):
        if self.measurement_timer and self.measurement_timer.isActive():
            self.measurement_timer.stop()
        if self.measurement_line:
            self.measurement_line.remove()
            self.measurement_line = None
            self.canvas.draw_idle()
        self.start_button.setEnabled(True)
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None


# ------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()