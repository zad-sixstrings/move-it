import os
import shutil
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QProgressBar, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class FileMoverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Move it!')
        self.setGeometry(100, 100, 600, 450)
        self.setFixedSize(600, 450)
        self.setWindowIcon(QIcon("move-it\\assets\\icon.ico"))

        self.setStyleSheet('''
            background-color: #333333;
            color: #c6c6c6;
        ''')

        main_layout = QVBoxLayout()

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Source folder layout
        source_layout = self.create_folder_layout('Source Folder:', self.browse_source)
        self.source_entry = source_layout.itemAt(1).widget()  # Define self.source_entry
        main_layout.addLayout(source_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Destination folder layout
        destination_layout = self.create_folder_layout('Destination Folder:', self.browse_destination)
        self.destination_entry = destination_layout.itemAt(1).widget()  # Define self.destination_entry
        main_layout.addLayout(destination_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Extension field layout
        extension_layout = QVBoxLayout()
        extension_layout.addWidget(QLabel('File Extension(s):', self))
        self.extension_entry = self.create_text_field(100, "jpg, mp3...")
        extension_layout.addWidget(self.extension_entry)
        main_layout.addLayout(extension_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Move it button layout
        moveit_layout = QHBoxLayout()
        self.move_button = self.create_button('Move it!', self.confirm_move_files)
        moveit_layout.addWidget(self.move_button)
        main_layout.addLayout(moveit_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Log text layout
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText('Welcome to Move it!\n\n\
Select source and destination folders, then type in the file extensions you want to filter (without the "." dot and separated by commas) and click the "Move it!" \
button to start moving your files.\n\nPro tip : Leave the file extensions field empty to move every file in the source folder. Only files will be moved, not folders.')
        # The default scrollbar gives me anxiety
        self.log_text.verticalScrollBar().setStyleSheet('''
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #c6c6c6;
                border-radius: 5px;
                border: 1px solid transparent;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: transparent;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        ''')
        log_layout.addWidget(self.log_text)
        main_layout.addLayout(log_layout)

        # Progress bar layout
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #7090b3;
                border: none;
                height: 30px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #007BFF;
                width: 1px;
            }
        ''')
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)

    def create_folder_layout(self, label_text, browse_function):
        folder_layout = QHBoxLayout()
        label = QLabel(label_text, self)
        folder_entry = self.create_text_field(350)
        browse_button = self.create_button('Browse...', browse_function)
        folder_layout.addWidget(label)
        folder_layout.addWidget(folder_entry)
        folder_layout.addWidget(browse_button)
        return folder_layout

    def create_text_field(self, width, placeholder_text=""):
        text_field = QLineEdit(self)
        text_field.setFixedWidth(width)
        text_field.setStyleSheet('''
            border: 1px solid #c6c6c6;
            border-radius: 2px;
            padding: 5px 5px;
        ''')
        text_field.setPlaceholderText(placeholder_text)
        return text_field

    def create_button(self, text, click_function):
        button = QPushButton(text, self)
        button.setStyleSheet('''
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:pressed {
            background-color: #003d80;
        }
        ''')
        button.setFocusPolicy(Qt.TabFocus)
        button.clicked.connect(click_function)
        return button

    # Confirmation pop-up
    def confirm_move_files(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText('Do you want to overwrite existing files in the destination folder, if any ? By clicking "No", moved files will be renamed and moved to the destination folder.')
        msg.setWindowTitle("Confirmation")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
        result = msg.exec_()

        if result == QMessageBox.Yes:
            self.move_files(overwrite=True)
        elif result == QMessageBox.No:
            self.move_files(overwrite=False)
        elif result == QMessageBox.Abort:
            self.log_text.append("File moving operation aborted.")
        else:
            pass

    def move_files(self, overwrite=False):
        source_folder, destination_folder, file_extensions = self.source_entry.text(), self.destination_entry.text(), self.extension_entry.text().split(',')
        
        # Check if both folders were picked
        if not source_folder or not destination_folder:
            self.log_text.append('<font color="#f7965e">Please provide source folder and destination folder.</font>')
            return

        # Check if both folders are the same
        if source_folder == destination_folder:
            self.log_text.append('<font color="#f7965e">Source and destination folders cannot be the same.</font>')
            return

        # Check if the source folder exists
        if not os.path.exists(source_folder):
            self.log_text.append('<font color="#f7965e">Source folder does not exist.</font>')
            return

        # Filter the files and count them
        def has_valid_extension(filename):
            return not file_extensions or any(filename.lower().endswith(ext.strip().lower()) for ext in file_extensions)

        filtered_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f)) and has_valid_extension(f)]
        total_filtered_files = len(filtered_files)

        files_moved, found_files = 0, False

        # Check if destination folder exists
        if not os.path.exists(destination_folder):
            self.log_text.append('<font color="#f7965e">Destination folder does not exist.</font>')
            return

        # Main loop
        for root, dirs, files in os.walk(source_folder):
            for filename in files:
                if has_valid_extension(filename):
                    found_files = True  # Set the flag to True if any files are found
                    source_path = os.path.join(root, filename)
                    destination_path = os.path.join(destination_folder, filename)

                    if not overwrite and os.path.exists(destination_path):
                        # No overwriting
                        new_filename = self.generate_unique_filename(destination_folder, filename)
                        destination_path = os.path.join(destination_folder, new_filename)
                        log_message = 'Moved <font color="lightyellow">{filename}</font> as <font color="lightblue">{new_filename}</font> in <font color="lightblue">{destination_folder}</font>'.format(filename=filename, new_filename=new_filename, destination_folder=destination_folder)
                    else:
                        log_message = 'Moved <font color="lightyellow">{filename}</font> to <font color="lightblue">{destination_folder}</font>'.format(filename=filename, destination_folder=destination_folder)

                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                    try:
                        shutil.move(source_path, destination_path)
                        self.log_text.append(log_message)
                        files_moved += 1
                        # Update the progress bar
                        self.progress_bar.setValue(int((files_moved / total_filtered_files) * 100))
                    except Exception as e:
                        # Exception handling
                        error_message = f'Error moving {filename}: {str(e)}'
                        self.log_text.append('<font color="#f7965e">' + error_message + '</font>')

        if not found_files:
            self.log_text.append('<font color="#f7965e">No files with such extension found.</font>')
        else:
            self.log_text.append(f'<font color="#adf75e">Files moved successfully ! ({files_moved} files)</font>')

    # Handle filenaming when not overwriting
    def generate_unique_filename(self, destination_folder, filename):
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{base_name}_{counter}{ext}"
            new_path = os.path.join(destination_folder, new_filename)
            if not os.path.exists(new_path):
                return new_filename
            counter += 1

    def browse_source(self):
        source_folder = QFileDialog.getExistingDirectory(self, 'Select Source Folder')
        self.source_entry.setText(source_folder)

    def browse_destination(self):
        destination_folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        self.destination_entry.setText(destination_folder)

if __name__ == '__main__': 
    app = QApplication(sys.argv)
    window = FileMoverApp()
    window.show()
    sys.exit(app.exec_())