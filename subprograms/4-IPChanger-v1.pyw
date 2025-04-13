import sys
import wmi
import ctypes
import os
import ipaddress
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout,
    QHBoxLayout, QMessageBox, QDialog, QLineEdit, QGridLayout, QGroupBox,
    QRadioButton, QButtonGroup, QToolTip
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Logging setup
LOG_FILE = "ip_changer.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def validate_ip(ip):
    """Validate an IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

class IPChanger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IP Changer')
        self.initUI()
        self.load_adapters()

    def initUI(self):
        self.setStyleSheet("""
            QLabel { font-size: 14px; }
            QPushButton { font-size: 14px; background-color: #5A9; padding: 5px; }
            QComboBox { font-size: 14px; }
        """)
        
        # Adapter selection
        adapter_label = QLabel('Select the network adapter you would like to change the IP:')
        self.adapter_combo = QComboBox()
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.load_adapters)
        adapter_layout = QHBoxLayout()
        adapter_layout.addWidget(self.adapter_combo)
        adapter_layout.addWidget(self.refresh_button)

        # Connect adapter selection change to update IP info
        self.adapter_combo.currentIndexChanged.connect(self.update_ip_config_display)

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

        # IP Configuration display
        self.ip_config_label = QLabel('Current IP Configuration:\n')
        self.ip_config_label.setStyleSheet("QLabel { background-color : lightgrey; padding: 5px; font-size: 12px; }")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(adapter_label)
        main_layout.addLayout(adapter_layout)
        main_layout.addWidget(scheme_label)
        main_layout.addWidget(scheme_box)
        main_layout.addWidget(self.set_button)
        main_layout.addWidget(self.ip_config_label)
        self.setLayout(main_layout)

    def load_adapters(self):
        self.adapter_combo.blockSignals(True)  # Prevent signals during loading
        self.adapter_combo.clear()
        c = wmi.WMI()
        adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        for adapter in adapters:
            self.adapter_combo.addItem(adapter.Description, adapter)
        self.adapter_combo.blockSignals(False)
        self.update_ip_config_display()

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
                logging.info(f"Adapter '{adapter.Description}' set to DHCP.")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to set DHCP:\n{e}')
                logging.error(f"Failed to set DHCP for adapter '{adapter.Description}': {e}")
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
                logging.info(f"Adapter '{adapter.Description}' set to IP {ip}.")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to set IP:\n{e}')
                logging.error(f"Failed to set IP for adapter '{adapter.Description}': {e}")
        self.update_ip_config_display()

    def open_manual_dialog(self, adapter):
        dialog = ManualIPDialog(adapter, self)
        dialog.exec_()
        self.update_ip_config_display()

    def update_ip_config_display(self):
        adapter = self.adapter_combo.currentData()
        if not adapter:
            self.ip_config_label.setText('Current IP Configuration:\nNo adapter selected.')
            return
        ip_info = f'Current IP Configuration for {adapter.Description}:\n'
        ip_addresses = adapter.IPAddress if adapter.IPAddress else ['Not set']
        subnet_masks = adapter.IPSubnet if adapter.IPSubnet else ['Not set']
        gateways = adapter.DefaultIPGateway if adapter.DefaultIPGateway else ['Not set']
        ip_info += f'IP Address: {", ".join(ip_addresses)}\n'
        ip_info += f'Subnet Mask: {", ".join(subnet_masks)}\n'
        ip_info += f'Gateway: {", ".join(gateways)}'
        self.ip_config_label.setText(ip_info)

class ManualIPDialog(QDialog):
    def __init__(self, adapter, parent=None):
        super().__init__(parent)
        self.adapter = adapter
        self.setWindowTitle('Manual IP Configuration')
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        self.ip_edits, ip_layout = self.create_ip_input('IP Address:', layout, 0)
        self.subnet_edits, subnet_layout = self.create_ip_input('Subnet Mask:', layout, 1)
        self.gateway_edits, gateway_layout = self.create_ip_input('Gateway:', layout, 2)

        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.set_manual_ip)
        layout.addWidget(self.ok_button, 3, 0, 1, 2)
        self.setLayout(layout)

    def create_ip_input(self, label_text, layout, row):
        label = QLabel(label_text)
        edits = [QLineEdit() for _ in range(4)]
        input_layout = QHBoxLayout()
        for i, edit in enumerate(edits):
            edit.setFixedWidth(50)
            edit.setMaxLength(3)
            edit.setAlignment(Qt.AlignCenter)
            input_layout.addWidget(edit)
            if i < 3:
                input_layout.addWidget(QLabel('.'))
        layout.addWidget(label, row, 0)
        layout.addLayout(input_layout, row, 1)
        return edits, input_layout

    def set_manual_ip(self):
        ip = '.'.join([edit.text() for edit in self.ip_edits])
        subnet = '.'.join([edit.text() for edit in self.subnet_edits])
        gateway = '.'.join([edit.text() for edit in self.gateway_edits])
        if not validate_ip(ip) or not validate_ip(subnet):
            QMessageBox.warning(self, 'Error', 'Invalid IP or Subnet Mask.')
            return
        try:
            res1 = self.adapter.EnableStatic(IPAddress=[ip], SubnetMask=[subnet])
            if gateway.strip('.'):
                res2 = self.adapter.SetGateways(DefaultIPGateway=[gateway])
            else:
                res2 = self.adapter.SetGateways(DefaultIPGateway=[])
            QMessageBox.information(self, 'Success', f'Adapter IP set to {ip}.')
            logging.info(f"Manual IP set for adapter '{self.adapter.Description}': IP={ip}, Subnet={subnet}, Gateway={gateway}")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to set IP:\n{e}')
            logging.error(f"Failed to set manual IP for adapter '{self.adapter.Description}': {e}")

if __name__ == '__main__':
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '"' + os.path.abspath(__file__) + '"', None, 1)
        sys.exit()

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
