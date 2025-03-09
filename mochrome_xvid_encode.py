import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import subprocess

class VideoEncoderApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FFmpeg Video Encoder for Casio Cassiopeia E-15')
        self.setGeometry(200, 200, 800, 400)
        
        self.initUI()
        self.jobs = []

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Input File/Folder Selection
        input_layout = QtWidgets.QHBoxLayout()
        self.input_path = QtWidgets.QLineEdit(self)
        self.input_path.setPlaceholderText('Select input file or folder...')
        input_button = QtWidgets.QPushButton('Browse...', self)
        input_button.clicked.connect(self.select_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_button)

        # Output Directory Selection
        output_layout = QtWidgets.QHBoxLayout()
        self.output_path = QtWidgets.QLineEdit(self)
        self.output_path.setPlaceholderText('Select output directory...')
        output_button = QtWidgets.QPushButton('Browse...', self)
        output_button.clicked.connect(self.select_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_button)

        # Job List
        self.job_list = QtWidgets.QListWidget(self)
        
        # Job Controls
        job_controls = QtWidgets.QHBoxLayout()
        self.resolution_dropdown = QtWidgets.QComboBox(self)
        self.fps_input = QtWidgets.QSpinBox(self)
        self.fps_input.setRange(5, 15)
        self.fps_input.setValue(5)
        
        self.downscale_filter = QtWidgets.QComboBox(self)
        self.downscale_filter.addItems(['Lanczos', 'Spline36', 'None'])
        
        self.preset = QtWidgets.QComboBox(self)
        self.preset.addItems(['None', 'No B-Frames', 'Tweaked'])
        
        self.run_checkbox = QtWidgets.QCheckBox('Run', self)
        
        add_button = QtWidgets.QPushButton('Add Job', self)
        add_button.clicked.connect(self.add_job)
        
        remove_button = QtWidgets.QPushButton('Remove Selected Job', self)
        remove_button.clicked.connect(self.remove_selected_job)
        
        job_controls.addWidget(self.resolution_dropdown)
        job_controls.addWidget(self.fps_input)
        job_controls.addWidget(self.downscale_filter)
        job_controls.addWidget(self.preset)
        job_controls.addWidget(self.run_checkbox)
        job_controls.addWidget(add_button)
        job_controls.addWidget(remove_button)

        # Run Controls
        run_controls = QtWidgets.QHBoxLayout()
        run_button = QtWidgets.QPushButton('Run', self)
        run_button.clicked.connect(self.run_jobs)
        
        clear_button = QtWidgets.QPushButton('Clear', self)
        clear_button.clicked.connect(self.clear_jobs)
        
        run_controls.addWidget(run_button)
        run_controls.addWidget(clear_button)

        # Status Log
        self.status_log = QtWidgets.QTextEdit(self)
        self.status_log.setReadOnly(True)
        
        # Add Widgets to Layout
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.job_list)
        layout.addLayout(job_controls)
        layout.addLayout(run_controls)
        layout.addWidget(self.status_log)

    def select_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Input File')
        if file_path:
            self.input_path.setText(file_path)
            self.update_resolutions((640, 480))  # Placeholder for aspect-ratio-based resolution handling.

    def select_output(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if folder_path:
            self.output_path.setText(folder_path)

    def update_resolutions(self, source_res):
        resolutions = [
            "240x180", "224x168", "208x156", "192x144",
            "176x132", "160x120", "144x108", "128x96"
        ]
        self.resolution_dropdown.clear()
        self.resolution_dropdown.addItems(resolutions)

    def add_job(self):
        resolution = self.resolution_dropdown.currentText()
        fps = self.fps_input.value()
        downscale = self.downscale_filter.currentText()
        preset = self.preset.currentText()
        run = self.run_checkbox.isChecked()
        
        job_text = f"{resolution} | {fps} FPS | {downscale} | {preset} | {'Run' if run else 'Skip'}"
        self.job_list.addItem(job_text)
        self.jobs.append((resolution, fps, downscale, preset, run))

    def remove_selected_job(self):
        selected = self.job_list.currentRow()
        if selected >= 0:
            self.job_list.takeItem(selected)
            self.jobs.pop(selected)

    def clear_jobs(self):
        self.job_list.clear()
        self.jobs = []

    def run_jobs(self):
        input_path = self.input_path.text()
        output_dir = self.output_path.text()

        if not input_path or not output_dir:
            self.status_log.append('Error: Input and output paths must be set.')
            return

        for resolution, fps, downscale, preset, run in self.jobs:
            if not run:
                continue

            # Determine suffixes for preset and downscale filter
            preset_suffix = ""
            filter_suffix = ""

            if preset == "No B-Frames":
                preset_suffix = "_nobf"
            elif preset == "Tweaked":
                preset_suffix = "_tweaked"

            if downscale in ["Lanczos", "Spline36"]:
                filter_suffix = f"_{downscale.lower()}"

            output_file = f"{output_dir}/{resolution}/{os.path.basename(input_path).replace('.mkv', f'-{resolution}-{fps}fps{preset_suffix}{filter_suffix}.avi')}"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            command_templates = {
                "None": (
                    'ffmpeg -i "{input_file}" -vf "scale={resolution}:flags={filter},fps={fps},format=gray,lut=y=\'(val/16)*16\'" '
                    '-c:v libxvid -q:v 3 -c:a adpcm_ima_wav -ar 8000 -ac 1 "{output_file}"'
                ),
                "No B-Frames": (
                    'ffmpeg -i "{input_file}" -vf "scale={resolution}:flags={filter},fps={fps},format=gray,lut=y=\'(val/16)*16\'" '
                    '-c:v libxvid -q:v 3 -bf 0 -c:a adpcm_ima_wav -ar 8000 -ac 1 "{output_file}"'
                ),
                "Tweaked": (
                    'ffmpeg -i "{input_file}" -vf "scale={resolution}:flags={filter},fps={fps},format=gray,lut=y=\'(val/16)*16\'" '
                    '-c:v libxvid -qscale:v 5 -bf 0 -g 10 '
                    '-maxrate 200k -bufsize 100k '
                    '-c:a adpcm_ima_wav -ar 8000 -ac 1 "{output_file}"'
                )
            }

            ffmpeg_command = command_templates[preset].format(
                input_file=input_path,
                resolution=resolution,
                filter=downscale.lower(),
                fps=fps,
                output_file=output_file
            )

            self.status_log.append(f"Running: {ffmpeg_command}")
            QtWidgets.QApplication.processEvents()

            subprocess.run(ffmpeg_command, shell=True, text=True)

        self.status_log.append("All jobs completed.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = VideoEncoderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
