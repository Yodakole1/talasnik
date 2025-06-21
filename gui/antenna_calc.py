import requests
from PyQt5.QtWidgets import QDialog, QFormLayout, QComboBox, QLineEdit, QSpinBox, QPushButton, QLabel
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QPalette
from PyQt5.QtCore import Qt

class AntennaCalculatorDialog(QDialog):
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Antenna Calculator")
        self.resize(420, 360)
        layout = QFormLayout(self)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Dipole",
            "Inverted V Dipole",
            "Quarter-Wave Ground Plane",
            "5/8 Wave Ground Plane",
            "Yagi-Uda",
            "J-Pole",
            "Slim Jim",
            "Delta Loop",
            "Half-Wave Vertical Dipole",
            "Helical"
        ])
        self.type_combo.currentTextChanged.connect(self.update_elements_visibility)
        layout.addRow("Antenna type:", self.type_combo)

        self.freq_edit = QLineEdit()
        self.freq_edit.setPlaceholderText("MHz (e.g. 145.5)")
        layout.addRow("Frequency (MHz):", self.freq_edit)

        self.elements_edit = QSpinBox()
        self.elements_edit.setRange(3, 20)
        self.elements_edit.setValue(4)
        layout.addRow("Number of elements:", self.elements_edit)

        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.clicked.connect(self.calculate)
        layout.addRow(self.calc_btn)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        layout.addRow(self.result_label)

        self.pic_label = QLabel()
        self.pic_label.setFixedSize(380, 140)
        layout.addRow(self.pic_label)

        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        if dark_mode:
            self.setStyleSheet("""
                QDialog, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton {
                    color: white;
                    background-color: #222;
                }
                QLineEdit, QComboBox, QSpinBox {
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton {
                    font-size: 14pt;
                }
            """)
        self.update_elements_visibility(self.type_combo.currentText())

    def update_elements_visibility(self, ant_type):
        # Only show elements for Yagi-Uda
        self.elements_edit.setVisible(ant_type == "Yagi-Uda")

    def calculate(self):
        ant_type = self.type_combo.currentText()
        freq_text = self.freq_edit.text().strip()
        if not freq_text:
            self.result_label.setText("Please input a frequency in the Frequency (MHz) field.")
            self.pic_label.clear()
            return
        try:
            freq = float(freq_text)
            if freq <= 0:
                raise ValueError
        except Exception:
            self.result_label.setText("Please input a valid frequency in the Frequency (MHz) field.")
            self.pic_label.clear()
            return

        elements = self.elements_edit.value() if ant_type == "Yagi-Uda" else None
        result = ""
        drawing_func = None
        total_al_m = 0

        c = 299_792_458  # speed of light in m/s

        try:
            if ant_type == "Dipole":
                # L = 143 / f (meters)
                total_len_m = 143 / freq
                total_len_cm = total_len_m * 100
                leg_m = total_len_m / 2
                leg_cm = total_len_cm / 2
                total_al_m = total_len_m
                result = (
                    f"<b>Total length:</b> {total_len_m:.2f} m ({total_len_cm:.2f} cm)<br>"
                    f"<b>Each leg:</b> {leg_m:.2f} m ({leg_cm:.2f} cm)"
                )
                drawing_func = self.draw_dipole

            elif ant_type == "Inverted V Dipole":
                total_len_m = 143 / freq
                leg_m = (total_len_m / 2) * 0.96  # 4% shorter
                total_al_m = leg_m * 2
                result = (
                    f"<b>Total length:</b> {total_len_m:.2f} m<br>"
                    f"<b>Each leg (corrected):</b> {leg_m:.2f} m"
                )
                drawing_func = self.draw_inverted_v

            elif ant_type == "Quarter-Wave Ground Plane":
                # λ = c / (f * 1e6)
                wavelength = c / (freq * 1e6)
                vertical_m = wavelength / 4
                radial_m = vertical_m * 1.05
                total_al_m = vertical_m + radial_m * 4
                result = (
                    f"<b>Vertical element:</b> {vertical_m:.2f} m<br>"
                    f"<b>Radials (each):</b> {radial_m:.2f} m"
                )
                drawing_func = self.draw_ground_plane

            elif ant_type == "5/8 Wave Ground Plane":
                wavelength = c / (freq * 1e6)
                vertical_m = wavelength * 0.625
                radial_m = (wavelength / 4) * 1.05
                total_al_m = vertical_m + radial_m * 4
                result = (
                    f"<b>Vertical element (5/8λ):</b> {vertical_m:.2f} m<br>"
                    f"<b>Radials (each):</b> {radial_m:.2f} m"
                )
                drawing_func = self.draw_ground_plane_58

            elif ant_type == "Yagi-Uda":
                wavelength = c / (freq * 1e6)
                reflector = 0.55 * wavelength
                driven = 0.5 * wavelength
                directors = []
                for n in range(elements - 2):
                    k = 0.48 - 0.01 * n  # D1=0.48, D2=0.47, etc.
                    directors.append(k * wavelength)
                spacing = 0.15 * wavelength
                boom = spacing * (elements - 1)
                total_al_m = reflector + driven + sum(directors) + boom
                result = (
                    f"<b>Wavelength:</b> {wavelength:.2f} m<br>"
                    f"<b>Reflector:</b> {reflector:.2f} m<br>"
                    f"<b>Driven:</b> {driven:.2f} m<br>"
                )
                for i, dlen in enumerate(directors):
                    result += f"<b>Director {i+1}:</b> {dlen:.2f} m<br>"
                result += (
                    f"<b>Element spacing:</b> {spacing:.2f} m<br>"
                    f"<b>Boom length:</b> {boom:.2f} m"
                )
                drawing_func = lambda: self.draw_yagi(reflector*100, driven*100, [d*100 for d in directors], spacing*100)

            elif ant_type == "J-Pole":
                wavelength = c / (freq * 1e6)
                long_elem = 0.75 * wavelength
                short_elem = 0.25 * wavelength
                total_al_m = long_elem + short_elem
                result = (
                    f"<b>Long element (3/4λ):</b> {long_elem:.2f} m<br>"
                    f"<b>Short element (1/4λ):</b> {short_elem:.2f} m<br>"
                    f"<b>Spacing:</b> 2.5–5 cm"
                )
                drawing_func = self.draw_jpole

            elif ant_type == "Slim Jim":
                wavelength = c / (freq * 1e6)
                total_len = 0.75 * wavelength
                match_section = 0.25 * wavelength
                total_al_m = total_len
                result = (
                    f"<b>Total length (3/4λ):</b> {total_len:.2f} m<br>"
                    f"<b>Matching section (1/4λ):</b> {match_section:.2f} m"
                )
                drawing_func = self.draw_slim_jim

            elif ant_type == "Delta Loop":
                wavelength = c / (freq * 1e6)
                perimeter = wavelength
                side = perimeter / 3
                total_al_m = perimeter
                result = (
                    f"<b>Perimeter (1λ):</b> {perimeter:.2f} m<br>"
                    f"<b>Each side:</b> {side:.2f} m"
                )
                drawing_func = lambda: self.draw_delta_loop(side*100)

            elif ant_type == "Half-Wave Vertical Dipole":
                wavelength = c / (freq * 1e6)
                total_len = 0.5 * wavelength
                total_al_m = total_len
                result = (
                    f"<b>Total length (1/2λ):</b> {total_len:.2f} m<br>"
                    f"<b>Each leg:</b> {total_len/2:.2f} m"
                )
                drawing_func = self.draw_vertical_dipole

            elif ant_type == "Helical":
                wavelength = c / (freq * 1e6)
                wire_len = 0.5 * wavelength
                total_al_m = wire_len
                result = (
                    f"<b>Wire length (1/2λ):</b> {wire_len:.2f} m<br>"
                    f"<b>Coil spacing, diameter, turns: depends on design</b>"
                )
                drawing_func = self.draw_helical

            else:
                result = "Unknown antenna type."
                self.pic_label.clear()
                return

            # --- Price calculation for all antennas ---
            try:
                r = requests.get("https://metals-api.com/api/latest?access_key=demo&base=USD&symbols=ALUMINUM", timeout=3)
                price = r.json()["rates"]["ALUMINUM"]
            except Exception:
                price = 2.5
            weight = total_al_m * 0.5  # 0.5 kg per meter
            cost = weight * price
            result += (
                f"<br><b>Total aluminum:</b> {total_al_m:.2f} m"
                f"<br><b>Estimated weight:</b> {weight:.2f} kg"
                f"<br><b>Aluminum price:</b> ${price:.2f}/kg"
                f"<br><b>Estimated cost:</b> ${cost:.2f}"
            )

            self.result_label.setText(result)
            if drawing_func:
                drawing_func()
        except Exception as e:
            self.result_label.setText(f"<span style='color:red'>Error: {e}</span>")
            self.pic_label.clear()

    def draw_dipole(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        try:
            freq = float(self.freq_edit.text())
            total_len_m = 143 / freq
            total_len_cm = total_len_m * 100
        except Exception:
            total_len_cm = 100  # fallback
        margin = 20
        max_len_px = w - 2 * margin
        scale = max_len_px / total_len_cm if total_len_cm else 1
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        try:
            pen = QPen(Qt.blue, 4)
            p.setPen(pen)
            x1 = margin
            x2 = margin + int(total_len_cm * scale)
            y = h // 2
            p.drawLine(x1, y, x2, y)
            p.setPen(QPen(Qt.red, 6))
            p.drawPoint((x1 + x2) // 2, y)
        finally:
            p.end()
        self.pic_label.setPixmap(pix)

    def draw_inverted_v(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        pen = QPen(Qt.blue, 4)
        p.setPen(pen)
        # Draw V shape
        p.drawLine(w//2, h//2, 20, h-20)
        p.drawLine(w//2, h//2, w-20, h-20)
        p.setPen(QPen(Qt.red, 6))
        p.drawPoint(w//2, h//2)
        p.end()
        self.pic_label.setPixmap(pix)

    def draw_ground_plane(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        # Vertical
        p.setPen(QPen(Qt.blue, 4))
        p.drawLine(w//2, h-20, w//2, 20)
        # Radials
        p.setPen(QPen(Qt.darkGreen, 3))
        for angle in [-45, -15, 15, 45]:
            import math
            x2 = w//2 + int(80 * math.cos(angle * 3.14/180))
            y2 = h-20 + int(80 * math.sin(angle * 3.14/180))
            p.drawLine(w//2, h-20, x2, y2)
        p.end()
        self.pic_label.setPixmap(pix)

    def draw_ground_plane_58(self):
        # Same as ground plane, but vertical is longer
        self.draw_ground_plane()

    def draw_yagi(self, reflector, driven, directors, spacing):
        # All arguments are in centimeters
        w, h = self.pic_label.width(), self.pic_label.height()
        margin = 20
        boom_len_cm = spacing * (len(directors) + 1)
        elem_lengths = [reflector, driven] + directors
        max_elem_cm = max(elem_lengths)
        boom_len_px = w - 2 * margin
        elem_max_px = h - 2 * margin
        scale_boom = boom_len_px / boom_len_cm if boom_len_cm else 1
        scale_elem = elem_max_px / max_elem_cm if max_elem_cm else 1

        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        boom_pen = QPen(Qt.darkGray, 5)
        painter.setPen(boom_pen)
        # Draw boom
        painter.drawLine(margin, h // 2, margin + int(boom_len_cm * scale_boom), h // 2)
        # Draw elements
        x = margin
        for i, elem_len in enumerate(elem_lengths):
            pen = QPen(Qt.black, 2)
            label = ""
            if i == 0:
                pen = QPen(Qt.red, 4)
                label = "R"
            elif i == 1:
                pen = QPen(Qt.blue, 4)
                label = "D"
            else:
                pen = QPen(Qt.black, 2)
                label = f"D{i-1}"
            painter.setPen(pen)
            elem_px = int(elem_len * scale_elem)
            y1 = h // 2 - elem_px // 2
            y2 = h // 2 + elem_px // 2
            painter.drawLine(int(x), y1, int(x), y2)
            painter.setPen(QPen(Qt.darkGreen, 1))
            painter.drawText(int(x) - 10, y1 - 8, label)
            x += spacing * scale_boom
        painter.end()
        self.pic_label.setPixmap(pix)

    def draw_jpole(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(QPen(Qt.blue, 4))
        # Long element
        p.drawLine(w//2-20, h-20, w//2-20, 20)
        # Short element
        p.drawLine(w//2+20, h-20, w//2+20, h//2)
        # Bottom join
        p.drawLine(w//2-20, h-20, w//2+20, h-20)
        p.end()
        self.pic_label.setPixmap(pix)

    def draw_slim_jim(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        try:
            p.setPen(QPen(Qt.blue, 4))
            # Left vertical
            p.drawLine(w//2-20, h-20, w//2-20, 20)
            # Top horizontal
            p.drawLine(w//2-20, 20, w//2+20, 20)
            # Right vertical
            p.drawLine(w//2+20, 20, w//2+20, h-20)
            # Bottom: leave a gap in the middle (not connected)
            gap = 24  # width of the gap in pixels
            left_end = w//2-20
            right_end = w//2+20
            y_bottom = h-20
            # Draw left bottom segment
            p.drawLine(left_end, y_bottom, w//2 - gap//2, y_bottom)
            # Draw right bottom segment
            p.drawLine(w//2 + gap//2, y_bottom, right_end, y_bottom)
        finally:
            p.end()
        self.pic_label.setPixmap(pix)

    def draw_delta_loop(self, side):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        try:
            p.setPen(QPen(Qt.blue, 4))
            # Calculate triangle points
            top_x, top_y = w // 2, 20
            left_x, left_y = 20, h - 20
            right_x, right_y = w - 20, h - 20
            # Draw all three sides (fully connected)
            p.drawLine(top_x, top_y, left_x, left_y)
            p.drawLine(left_x, left_y, right_x, right_y)
            p.drawLine(right_x, right_y, top_x, top_y)
        finally:
            p.end()
        self.pic_label.setPixmap(pix)

    def draw_vertical_dipole(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(QPen(Qt.blue, 4))
        p.drawLine(w//2, 20, w//2, h-20)
        p.setPen(QPen(Qt.red, 6))
        p.drawPoint(w//2, h//2)
        p.end()
        self.pic_label.setPixmap(pix)

    def draw_helical(self):
        w, h = self.pic_label.width(), self.pic_label.height()
        pix = QPixmap(w, h)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(QPen(Qt.blue, 3))
        # Draw a spiral (approximate)
        import math
        cx, cy = w//2, h//2
        r = 10
        for t in range(0, 360*3, 10):
            angle = math.radians(t)
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle) * 0.5)
            if t == 0:
                last = (x, y)
            else:
                p.drawLine(last[0], last[1], x, y)
                last = (x, y)
            r += 0.5
        p.end()
        self.pic_label.setPixmap(pix)