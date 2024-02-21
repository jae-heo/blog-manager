import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel

server_ip = "http://3.35.102.165:8000"
headers = {"secret_code": "onyubabo"}

class LicenseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.client_id_input = QLineEdit(self)
        self.client_id_input.setPlaceholderText("Client ID")
        self.days_input = QLineEdit(self)
        self.days_input.setPlaceholderText("Days (for creating/updating license)")
        self.result_label = QLabel("Result will be shown here", self)

        self.create_btn = QPushButton("Create License", self)
        self.create_btn.clicked.connect(self.create_license)

        self.read_btn = QPushButton("Read License", self)
        self.read_btn.clicked.connect(self.read_license)

        self.update_btn = QPushButton("Update License", self)
        self.update_btn.clicked.connect(self.update_license)

        self.delete_btn = QPushButton("Delete License", self)
        self.delete_btn.clicked.connect(self.delete_license)

        self.layout.addWidget(self.client_id_input)
        self.layout.addWidget(self.days_input)
        self.layout.addWidget(self.create_btn)
        self.layout.addWidget(self.read_btn)
        self.layout.addWidget(self.update_btn)
        self.layout.addWidget(self.delete_btn)
        self.layout.addWidget(self.result_label)

        self.setLayout(self.layout)
        self.setWindowTitle('License Manager')

    def create_license(self):
        client_id = self.client_id_input.text()
        days = self.days_input.text()

        if client_id == "" or days == "":
            self.result_label.setText("ID와 Days를 입력해주세요.")
            return
        
        response = requests.post(f"{server_ip}/licenses", json={"client_id": client_id, "days": int(days)}, headers=headers)
        self.result_label.setText(response.json().get("message", ""))

    def read_license(self):
        client_id = self.client_id_input.text()
        if client_id == "":
            self.result_label.setText("ID를 입력해주세요.")
            return
        
        response = requests.get(f"{server_ip}/licenses/{client_id}", headers=headers)
        if response.status_code == 200:
            self.result_label.setText(str(response.json()))
        else:
            self.result_label.setText("License not found")

    def update_license(self):
        client_id = self.client_id_input.text()
        days = self.days_input.text()

        if client_id == "" or days == "":
            self.result_label.setText("ID와 Days를 입력해주세요.")
            return
        
        response = requests.put(f"{server_ip}/licenses/{client_id}", json={"days": int(days)}, headers=headers)
        self.result_label.setText(response.json().get("message", ""))

    def delete_license(self):
        client_id = self.client_id_input.text()
        if client_id == "":
            self.result_label.setText("ID를 입력해주세요.")
            return
        
        response = requests.delete(f"{server_ip}/licenses/{client_id}", headers=headers)
        self.result_label.setText(response.json().get("message", ""))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LicenseApp()
    ex.show()
    sys.exit(app.exec_())