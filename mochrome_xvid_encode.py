import sys
import os
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

class VideoEncoderApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FFmpeg Video Encoder for Casio Cassiopeia E-15')
        self.setGeometry(200, 200, 900, 450)

        self.initUI()
        self.jobs = []

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Input File Selection
        input_layout = QtWidgets.QHBoxLayout()
        self.input_path = QtWidgets.QLineEdit(self)
        self.input_path.setPlaceholderText('Select input file...')
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

        self.sample_rate = QtWidgets.QComboBox(self)
        self.sample_rate.addItems(['8000', '16000', '24000', '32000', '44100'])

        self.run_checkbox = QtWidgets.QCheckBox('Run', self)

        add_button = QtWidgets.QPushButton('Add Job', self)
        add_button.clicked.connect(self.add_job)

        remove_button = QtWidgets.QPushButton('Remove Job', self)
        remove_button.clicked.connect(self.remove_selected_job)

        job_controls.addWidget(self.resolution_dropdown)
        job_controls.addWidget(self.fps_input)
        job_controls.addWidget(self.downscale_filter)
        job_controls.addWidget(self.preset)
        job_controls.addWidget(self.sample_rate)
        job_controls.addWidget(self.run_checkbox)
        job_controls.addWidget(add_button)
        job_controls.addWidget(remove_button)

        # Run Controls
        run_controls = QtWidgets.QHBoxLayout()
        run_button = QtWidgets.QPushButton('Run', self)
        run_button.clicked.connect(self.run_jobs)

        clear_button = QtWidgets.QPushButton('Clear Jobs', self)
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

        self.setLayout(layout)

    def select_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Input File')
        if file_path:
            self.input_path.setText(file_path)
            self.detect_resolution(file_path)

    def select_output(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if folder_path:
            self.output_path.setText(folder_path)

    def detect_resolution(self, file_path):
   
