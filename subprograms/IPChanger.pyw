import sys
import wmi
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout,
    QHBoxLayout, QMessageBox, QDialog, QLineEdit, QGridLayout, QGroupBox,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt

class IPChanger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IP Changer')
        self.initUI()
        self.load_adapters()

    def initUI(self):
        # Adapter selection
        adapter_label = QLabel('Select the network adapter you would like to change the IP:')
        self.adapter_combo = QComboBox()
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.load_adapters)
        adapter_layout = QHBoxLayout()
        adapter_layout.addWidget(self.adapter_combo)
        adapter_layout.addWidget(self.refresh_button)

        # IP Scheme selection
        scheme_label = QLabel('Select what IP Scheme you would like to set:')
        self.scheme_group = QButtonGroup()
        schemes = ["DHCP", "Omnia", "SSOM", "Gilbarco 10.5 Subnet", "Veriphone", "Applause", "Veeder-Root", "Manual"]
        scheme_layout = QVBoxLayout()
        for scheme in schemes:
            radio = QRadioButton(scheme)
            self.scheme_group.addButton(radio)
            scheme_layout.addWidget(radio)
        scheme_box = QGroupBox()
        scheme_box.setLayout(scheme_layout)

        # Set button
        self.set_button = QPushButton('Set')
        self.set_button.clicked.connect(self.apply_settings)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(adapter_label)
        main_layout.addLayout(adapter_layout)
        main_layout.addWidget(scheme_label)
        main_layout.addWidget(scheme_box)
        main_layout.addWidget(self.set_button)
        self.setLayout(main_layout)

    def load_adapters(self):
        self.adapter_combo.clear()
        c = wmi.WMI()
        adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        for adapter in adapters:
            self.adapter_combo.addItem(adapter.Description, adapter)

    def apply_settings(self):
        adapter = self.adapter_combo.currentData()
        selected_scheme = None
        for button in self.scheme_group.buttons():
            if button.isChecked():
                selected_scheme = button.text()
                break
        if not selected_scheme:
            QMessageBox.warning(self, 'Error', 'Please select an IP Scheme.')
            return
        if not adapter:
            QMessageBox.warning(self, 'Error', 'Please select a network adapter.')
            return
        if selected_scheme == 'Manual':
            self.open_manual_dialog(adapter)
        else:
            self.set_ip(adapter, selected_scheme)

    def set_ip(self, adapter, scheme_name):
        if scheme_name == 'DHCP':
            try:
                res1 = adapter.EnableDHCP()
                res2 = adapter.SetDNSServerSearchOrder()
                QMessageBox.information(self, 'Success', 'Adapter set to DHCP.')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to set DHCP:\n{e}')
        else:
            scheme = ip_schemes.get(scheme_name)
            if not scheme:
                QMessageBox.warning(self, 'Error', 'Invalid IP scheme selected.')
                return
            ip = scheme['ip']
            subnet = scheme['subnet']
            gateway = scheme['gateway']
            try:
                res1 = adapter.EnableStatic(IPAddress=[ip], SubnetMask=[subnet])
                if gateway:
                    res2 = adapter.SetGateways(DefaultIPGateway=[gateway])
                else:
                    res2 = adapter.SetGateways(DefaultIPGateway=[])
                QMessageBox.information(self, 'Success', f'Adapter IP set to {ip}.')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to set IP:\n{e}')

    def open_manual_dialog(self, adapter):
        dialog = ManualIPDialog(adapter, self)
        dialog.exec_()

class ManualIPDialog(QDialog):
    def __init__(self, adapter, parent=None):
        super().__init__(parent)
        self.adapter = adapter
        self.setWindowTitle('Manual IP Configuration')
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        ip_label = QLabel('IP Address:')
        self.ip_edits = [QLineEdit() for _ in range(4)]
        ip_layout = QHBoxLayout()
        for i, edit in enumerate(self.ip_edits):
            edit.setFixedWidth(40)
            edit.setMaxLength(3)
            ip_layout.addWidget(edit)
            if i < 3:
                ip_layout.addWidget(QLabel('.'))

        subnet_label = QLabel('Subnet Mask:')
        self.subnet_edits = [QLineEdit() for _ in range(4)]
        subnet_layout = QHBoxLayout()
        for i, edit in enumerate(self.subnet_edits):
            edit.setFixedWidth(40)
            edit.setMaxLength(3)
            subnet_layout.addWidget(edit)
            if i < 3:
                subnet_layout.addWidget(QLabel('.'))

        gateway_label = QLabel('Gateway:')
        self.gateway_edits = [QLineEdit() for _ in range(4)]
        gateway_layout = QHBoxLayout()
        for i, edit in enumerate(self.gateway_edits):
            edit.setFixedWidth(40)
            edit.setMaxLength(3)
            gateway_layout.addWidget(edit)
            if i < 3:
                gateway_layout.addWidget(QLabel('.'))

        layout.addWidget(ip_label, 0, 0)
        layout.addLayout(ip_layout, 0, 1)
        layout.addWidget(subnet_label, 1, 0)
        layout.addLayout(subnet_layout, 1, 1)
        layout.addWidget(gateway_label, 2, 0)
        layout.addLayout(gateway_layout, 2, 1)

        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.set_manual_ip)
        layout.addWidget(self.ok_button, 3, 0, 1, 2)
        self.setLayout(layout)

    def set_manual_ip(self):
        ip = '.'.join([edit.text() for edit in self.ip_edits])
        subnet = '.'.join([edit.text() for edit in self.subnet_edits])
        gateway = '.'.join([edit.text() for edit in self.gateway_edits])
        if not ip or not subnet:
            QMessageBox.warning(self, 'Error', 'IP and Subnet Mask are required.')
            return
        try:
            res1 = self.adapter.EnableStatic(IPAddress=[ip], SubnetMask=[subnet])
            if gateway:
                res2 = self.adapter.SetGateways(DefaultIPGateway=[gateway])
            else:
                res2 = self.adapter.SetGateways(DefaultIPGateway=[])
            QMessageBox.information(self, 'Success', f'Adapter IP set to {ip}.')
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to set IP:\n{e}')

if __name__ == '__main__':
    ip_schemes = {
        "DHCP": "DHCP",
        "Omnia": {"ip": "172.20.100.198", "subnet": "255.255.255.0", "gateway": "172.20.100.254"},
        "SSOM": {"ip": "172.16.100.198", "subnet": "255.255.255.0", "gateway": "172.16.100.254"},
        "Gilbarco 10.5 Subnet": {"ip": "10.5.55.201", "subnet": "255.255.255.0", "gateway": None},
        "Veriphone": {"ip": "192.168.31.200", "subnet": "255.255.255.0", "gateway": None},
        "Applause": {"ip": "10.5.60.198", "subnet": "255.255.255.0", "gateway": "10.5.60.1"},
        "Veeder-Root": {"ip": "192.168.11.200", "subnet": "255.255.255.0", "gateway": None},
        "Manual": "Manual"
    }

    app = QApplication(sys.argv)
    window = IPChanger()
    window.show()
    sys.exit(app.exec_())
