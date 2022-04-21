"""
@file local_app.py
@author Ryan Missel
Entrypoint for the Bunkers & Badasses loot generator program (https://github.com/qu-gg/BnB-LootGenerator)
Handles all of the UI interaction and display for the PyQT frontend
"""
import os
import sys
from pathlib import Path

from classes.Gun import Gun
from classes.GunImage import GunImage
from generate_gun_cmd import generate_gun_pdf
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox, QLabel,
                             QLineEdit, QWidget, QPushButton, QCheckBox,QMainWindow)


class Window(QMainWindow):
    def __init__(self, basedir):
        super(Window, self).__init__()

        # Load classes
        self.basedir = basedir
        self.gun_images = GunImage(self.basedir)

        # Window Title
        self.setWindowTitle("Bunkers and Badasses - LootGenerator")

        ###################################
        ###  BEGIN: Base Stats Grid     ###
        ###################################
        base_stats_group = QGroupBox("Configuration")
        base_stats_layout = QGridLayout()
        base_stats_layout.setAlignment(Qt.AlignTop)

        # Add stat function
        def add_stat_to_layout(layout, label, row):
            """
            Adds all the necessary widgets to a grid layout for a single stat
            :param label: The label to display
            :param row: The row number to add on
            :param signal_function: An additional function to connect on edit
            :param force_int: Force input to be an integer value
            :param read_only: Make text field read only
            :returns: The QLineEdit object
            """
            new_label = QLabel(label)
            new_line_edit = QLineEdit()

            layout.addWidget(new_label, row, 0)
            layout.addWidget(new_line_edit, row, 1)
            return new_line_edit

        # Gun Name
        self.name_line_edit = add_stat_to_layout(base_stats_layout, "Gun Name:", 0)

        # Item Level
        base_stats_layout.addWidget(QLabel("Item Level: "), 1, 0)
        self.item_level_box = QComboBox()
        self.item_level_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/gun_types.json").get("pistol").keys():
            self.item_level_box.addItem(item)
        base_stats_layout.addWidget(self.item_level_box, 1, 1)

        # Gun Type
        self.gun_type_choices = ['pistol', 'submachine_gun', 'shotgun', 'combat_rifle', 'sniper_rifle', 'rocket_launcher']

        base_stats_layout.addWidget(QLabel("Gun Type: "), 2, 0)
        self.gun_type_box = QComboBox()
        self.gun_type_box.addItem("Random")
        for item in self.gun_type_choices:
            self.gun_type_box.addItem(item.capitalize().replace('_', ' '))
        base_stats_layout.addWidget(self.gun_type_box, 2, 1)

        # Guild
        base_stats_layout.addWidget(QLabel("Guild: "), 3, 0)
        self.guild_type_box = QComboBox()
        self.guild_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/guild_table.json").keys():
            self.guild_type_box.addItem(item.capitalize())
        base_stats_layout.addWidget(self.guild_type_box, 3, 1)

        # Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]

        base_stats_layout.addWidget(QLabel("Rarity: "), 4, 0)
        self.rarity_type_box = QComboBox()
        for item in rarities:
            self.rarity_type_box.addItem(item)
        base_stats_layout.addWidget(self.rarity_type_box, 4, 1)

        # Roll for Rarity
        element_roll_text_label = QLabel("Force an Element Roll: ")
        element_roll_text_label.setToolTip("Choose whether to always add an element roll regardless of the rarity rolled. "
                                           "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(element_roll_text_label, 5, 0)
        self.element_roll = QCheckBox()
        self.element_roll.setToolTip("Choose whether to always add an element roll regardless of the rarity rolled. "
                                           "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(self.element_roll, 5, 1)

        # Whether to use a gun prefix
        prefix_text_label = QLabel("Include a Prefix: ")
        prefix_text_label.setToolTip("Choose whether to roll a Prefix modifier to the gun, as per Page 99.")
        base_stats_layout.addWidget(prefix_text_label, 6, 0)
        self.gun_prefix = QCheckBox()
        self.gun_prefix.setToolTip("Choose whether to roll a Prefix modifier to the gun, as per Page 99.")
        base_stats_layout.addWidget(self.gun_prefix, 6, 1)

        # Whether to roll for Red Text on epic or legendary
        red_text_label = QLabel("Include Red Text: ")
        red_text_label.setToolTip("Choose whether to roll for a Red Text modifier on guns of rarity Epic or Legendary, as per Page 100.")
        base_stats_layout.addWidget(red_text_label, 7, 0)
        self.red_text = QCheckBox()
        self.red_text.setToolTip("Choose whether to roll for a Red Text modifier on guns of rarity Epic or Legendary, as per Page 100.")
        base_stats_layout.addWidget(self.red_text, 7, 1)

        base_stats_layout.addWidget(QLabel(""), 8, 0)

        # Whether to roll for Red Text on epic or legendary
        damage_balance_label = QLabel("Use RobMWJ's Damage Balance: ")
        damage_balance_label.setToolTip("Choose whether to use alternative damage tables, written by user/robmwj on Reddit.")
        base_stats_layout.addWidget(damage_balance_label, 9, 0)
        self.damage_balance_check = QCheckBox()
        self.damage_balance_check.setToolTip("Choose whether to use alternative damage tables, written by user/robmwj on Reddit.")
        base_stats_layout.addWidget(self.damage_balance_check, 9, 1)

        # Whether to roll for Red Text on epic or legendary
        rarity_border_label = QLabel("Use Gun Rarity Borders: ")
        rarity_border_label.setToolTip("EXPERIMENTAL: Choose whether to outline the gun art in a colored-outline based on rarity. Doesn't work for all guns currently.")
        base_stats_layout.addWidget(rarity_border_label, 10, 0)
        self.rarity_border_check = QCheckBox()
        self.rarity_border_check.setToolTip("EXPERIMENTAL: Choose whether to outline the gun art in a colored-outline based on rarity. Doesn't work for all guns currently.")
        base_stats_layout.addWidget(self.rarity_border_check, 10, 1)

        # Grid layout
        base_stats_group.setLayout(base_stats_layout)
        ###################################
        ###  END: Base Stats Grid       ###
        ###################################

        ###################################
        ###  START: Generation          ###
        ###################################
        generation_group = QGroupBox("Generation")
        generation_layout = QGridLayout()
        generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.pdf_line_edit = add_stat_to_layout(generation_layout, "PDF Filename:", 0)
        self.pdf_line_edit.setToolTip("Specify the filename that Generate Gun saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Gun")
        button.setToolTip("Handles generating the gun and locally saving the PDF in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_gun())
        generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.output_pdf_label = QLabel()
        generation_layout.addWidget(self.output_pdf_label, 2, 0, 1, -1)

        # Grid layout
        generation_group.setLayout(generation_layout)
        ###################################
        ###  END: Generation            ###
        ###################################

        ###################################
        ###  START: Gun Display         ###
        ###################################
        gun_card_group = QGroupBox("Gun Card")
        gun_card_layout = QGridLayout()
        gun_card_layout.setAlignment(Qt.AlignVCenter)

        self.WebBrowser = QAxContainer.QAxWidget(self)
        self.WebBrowser.setFixedHeight(800)
        self.WebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.WebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                   "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        gun_card_layout.addWidget(self.WebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_pdf = "EXAMPLE.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/EXAMPLE.pdf")).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        gun_card_group.setLayout(gun_card_layout)
        ###################################
        ###  START: Gun Display         ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(300)
        generation_group.setFixedWidth(300)
        gun_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(300)
        generation_group.setFixedHeight(500)
        gun_card_group.setFixedHeight(800)

        # Overall layout grid
        layout = QGridLayout()
        layout.addWidget(base_stats_group, 0, 0)
        layout.addWidget(generation_group, 1, 0)
        layout.addWidget(gun_card_group, 0, 1, -1, 1)

        # Setting layout to be the central widget of main window
        wid = QWidget()
        wid.setLayout(layout)
        self.setCentralWidget(wid)

    def generate_gun(self):
        """ Handles performing the call to generate a gun given the parameters and updating the Gun Card image """
        # Load in properties that are currently set in the program
        name = None if self.name_line_edit.text() == "" else self.name_line_edit.text()
        item_level = self.item_level_box.currentText().lower()

        gun_type = self.gun_type_box.currentText().lower().replace(' ', '_')    # Convert gun type to digit
        if gun_type != "random":
            gun_type = str(self.gun_type_choices.index(gun_type) + 1)

        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_roll = self.element_roll.isChecked()
        prefix = self.gun_prefix.isChecked()
        redtext = self.red_text.isChecked()

        damage_balance = self.damage_balance_check.isChecked()
        rarity_check = self.rarity_border_check.isChecked()

        # Generate the gun object
        gun = Gun(self.basedir, name=name, item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                  damage_balance=damage_balance, rarity_element=element_roll, prefix=prefix, redtext=redtext)

        # Generate the PDF output name as the gun name
        output_name = "{}_{}_{}_{}".format(
            gun.type.title().replace('_', ' '), gun.guild.title(), gun.rarity.title(), gun.name).replace(' ', '') \
            if self.pdf_line_edit.text() == "" else self.pdf_line_edit.text()

        # Check if it is already in use
        if output_name == self.current_pdf:
            self.output_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        self.output_pdf_label.setText("Saved to outputs/{}.pdf!".format(output_name))
        self.current_pdf = output_name

        # Generate the local gun card PDF
        generate_gun_pdf(self.basedir, output_name, gun, self.gun_images, rarity_check)

        # Load in gun card PDF
        f = Path(os.path.abspath("output/{}.pdf".format(output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)


if __name__ == '__main__':
    # Specify whether this is local development or applicatino compilation
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
