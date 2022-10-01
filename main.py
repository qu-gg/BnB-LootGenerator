"""
@file main.py
@author Ryan Missel

Entrypoint for the Bunkers & Badasses loot generator program (https://github.com/qu-gg/BnB-LootGenerator)
Handles the UI interaction and display for the PyQT frontend
"""
import sys

from app.GunTab import GunTab
from app.ShieldTab import ShieldTab
from app.RelicTab import RelicTab
from app.PotionTab import PotionTab
from app.GrenadeTab import GrenadeTab

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QStatusBar)


class Window(QMainWindow):
    def __init__(self, basedir):
        super(Window, self).__init__()

        # Load classes
        self.basedir = basedir

        # Window Title
        self.setWindowTitle("Bunkers and Badasses - LootGenerator")

        # Add a status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # TabWidget for the different generation menus
        self.tabMenu = QTabWidget()

        # Gun Tab
        self.gun_tab = GunTab(basedir, self.statusbar)
        self.tabMenu.addTab(self.gun_tab.get_tab(), "Gun")
        self.tabMenu.setTabText(0, "Guns")

        # Shield Tab
        self.shield_tab = ShieldTab(basedir)
        self.tabMenu.addTab(self.shield_tab.get_tab(), "Shield")
        self.tabMenu.setTabText(1, "Shields")

        # Relic Tab
        self.relic_tab = RelicTab(basedir)
        self.tabMenu.addTab(self.relic_tab.get_tab(), "Relic")
        self.tabMenu.setTabText(2, "Relics")

        # Potion Tab
        self.potion_tab = PotionTab(basedir)
        self.tabMenu.addTab(self.potion_tab.get_tab(), "Potion")
        self.tabMenu.setTabText(3, "Potions")

        # Grenade Tab
        self.grenade_tab = GrenadeTab(basedir)
        self.tabMenu.addTab(self.grenade_tab.get_tab(), "Grenade")
        self.tabMenu.setTabText(4, "Grenades")

        # Setting layout to be the central widget of main window
        self.setCentralWidget(self.tabMenu)


if __name__ == '__main__':
    # Specify whether this is local development or application compilation
    basedir = ""
    application = False

    # If application compilation, get the folder from which the executable is being executed
    if application:
        # First split depending on OS to get the current application name (in case users have modified it)
        if '/' in sys.executable:
            current_app_name = sys.executable.split('/')[-1]
        elif '\\' in sys.executable:
            current_app_name = sys.executable.split('\\')[-1]
        else:
            raise NotADirectoryError("Pathing not found for {}. Please move to another path!".format(sys.executable))

        # Then replace the application name with nothing to get the path
        basedir = sys.executable.replace(current_app_name, '')

    # Define the application
    app = QApplication(sys.argv)
    window = Window(basedir)

    # Different checking needed depending on local build or executable run
    window.setWindowIcon(QIcon('resources/images/LootGeneratorIconBlue.ico'))
    window.show()
    sys.exit(app.exec_())
