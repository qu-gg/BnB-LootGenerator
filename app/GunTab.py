"""
@file GunTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to gun generation
"""
import os
from pathlib import Path

from classes.Gun import Gun
from classes.GunPDF import GunPDF
from classes.GunImage import GunImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton, QCheckBox)


class GunTab(QWidget):
    def __init__(self, basedir):
        super(GunTab, self).__init__()

        # Load classes
        self.basedir = basedir

        # PDF and Image Classes
        self.gun_pdf = GunPDF(self.basedir)
        self.gun_images = GunImage(self.basedir)

        ###################################
        ###  BEGIN: Base Stats Grid     ###
        ###################################
        base_stats_group = QGroupBox("Configuration")
        base_stats_layout = QGridLayout()
        base_stats_layout.setAlignment(Qt.AlignTop)

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
        self.gun_type_choices = ['pistol', 'submachine_gun', 'shotgun',
                                 'combat_rifle', 'sniper_rifle', 'rocket_launcher']

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

        # Prefix: [None, Random, Selection]
        base_stats_layout.addWidget(QLabel("Prefix: "), 5, 0)
        self.prefix_box = QComboBox()
        self.prefix_box.addItem("None")
        self.prefix_box.addItem("Random")
        for pidx, (key, item) in enumerate(get_file_data(basedir + "resources/guns/prefix.json").items()):
            self.prefix_box.addItem(f"[{pidx + 1}] {item['name']}")
        self.prefix_box.setToolTip("Choose whether to add a random Prefix or a specific one")
        base_stats_layout.addWidget(self.prefix_box, 5, 1)

        # RedText: [None, Random, Selection]
        base_stats_layout.addWidget(QLabel("Red Text: "), 6, 0)
        self.redtext_box = QComboBox()
        self.redtext_box.addItem("None")
        self.redtext_box.addItem("Random (All Rarities)")
        self.redtext_box.addItem("Random (Epics+)")
        self.redtext_box.addItem("Random (Legendaries)")
        for key, item in get_file_data(basedir + "resources/guns/redtext.json").items():
            self.redtext_box.addItem(f"[{key}] {item['name']}")

        self.redtext_box.setCurrentIndex(3)
        self.redtext_box.setToolTip("Choose whether to add a random RedText for Epics/Legendaries or a specific one regardless of rarity")
        base_stats_layout.addWidget(self.redtext_box, 6, 1)

        # Gun Balance Table
        self.gun_balance_dict = {
            "Source Book": 'gun_types',
            "McCoby\'s": "gun_types_mccoby",
            "RobMWJ\'s": "gun_types_robmwj"
        }
        balance_label = QLabel("Damage Balance Sheet: ")
        balance_label.setToolTip("Choose which Gun Damage Balance system to use - either the source book\'s or homebrew alternatives.")
        base_stats_layout.addWidget(balance_label, 7, 0)
        self.gun_balance_box = QComboBox()
        for item in self.gun_balance_dict.keys():
            self.gun_balance_box.addItem(item)
        base_stats_layout.addWidget(self.gun_balance_box, 7, 1)

        # Whether to hide Red Text Effects
        hide_redtext_label = QLabel("Hide Red Text Effect: ")
        hide_redtext_label.setToolTip("Whether to show the text but high the effect for Red Texts")
        base_stats_layout.addWidget(hide_redtext_label, 8, 0)
        self.hide_redtext_check = QCheckBox()
        self.hide_redtext_check.setToolTip("Whether to show the text but high the effect for Red Texts")
        base_stats_layout.addWidget(self.hide_redtext_check, 8, 1)

        # Whether to force an element roll on the table
        element_roll_text_label = QLabel("Force an Element Roll: ")
        element_roll_text_label.setToolTip(
            "Choose whether to always add an element roll regardless of the rarity rolled. "
            "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(element_roll_text_label, 9, 0)
        self.element_roll = QCheckBox()
        self.element_roll.setToolTip("Choose whether to always add an element roll regardless of the rarity rolled. "
                                     "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(self.element_roll, 9, 1)

        # Whether to roll for Red Text on epic or legendary
        rarity_border_label = QLabel("Use Gun Color Splashes: ")
        rarity_border_label.setToolTip("Choose whether to outline the gun art in a colored-outline based on rarity.")
        base_stats_layout.addWidget(rarity_border_label, 10, 0)
        self.rarity_border_check = QCheckBox()
        self.rarity_border_check.setToolTip("Choose whether to outline the gun art in a colored-outline based on rarity.")
        self.rarity_border_check.setChecked(True)
        base_stats_layout.addWidget(self.rarity_border_check, 10, 1)

        # Grid layout
        base_stats_group.setLayout(base_stats_layout)
        ###################################
        ###  END: Base Stats Grid       ###
        ###################################

        ###################################
        ###  START: Generation          ###
        ###################################
        generation_group = QGroupBox("Single-Gun Generation")
        generation_layout = QGridLayout()
        generation_layout.setAlignment(Qt.AlignTop)

        # Whether to save the PDF as form-fillable still
        form_fill_label = QLabel("Keep PDF Form-Fillable:")
        form_fill_label.setToolTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        generation_layout.addWidget(form_fill_label, 0, 0)
        self.form_fill_check = QCheckBox()
        self.form_fill_check.setToolTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        generation_layout.addWidget(self.form_fill_check, 0, 1)

        # Whether to save the PDF as form-fillable still
        form_design_label = QLabel("Use 2-Page Design:")
        form_design_label.setToolTip("Chooses whether to use the single card or two page card designs for output.")
        generation_layout.addWidget(form_design_label, 1, 0)
        self.form_design_check = QCheckBox()
        self.form_design_check.setToolTip("Chooses whether to use the single card or two page card designs for output.")
        generation_layout.addWidget(self.form_design_check, 1, 1)

        # PDF Output Name
        self.pdf_line_edit = add_stat_to_layout(generation_layout, "PDF Filename:", 2)
        self.pdf_line_edit.setToolTip("Specify the filename that Generate Gun saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Gun")
        button.setToolTip("Handles generating the gun and locally saving the PDF in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_gun())
        generation_layout.addWidget(button, 3, 0, 1, -1)

        # Label for savefile output
        self.output_pdf_label = QLabel()
        generation_layout.addWidget(self.output_pdf_label, 4, 0, 1, -1)

        # Grid layout
        generation_group.setLayout(generation_layout)
        ###################################
        ###  END: Generation            ###
        ###################################

        ###################################
        ###  START: Multi Generation    ###
        ###################################
        multi_group = QGroupBox("Multi-Gun Generation")
        multi_layout = QGridLayout()
        multi_layout.setAlignment(Qt.AlignTop)

        # Whether to save the PDF as form-fillable still
        multi_fill_label = QLabel("Keep PDF Form-Fillable:")
        multi_fill_label.setToolTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        multi_layout.addWidget(multi_fill_label, 0, 0)
        self.multi_fill_check = QCheckBox()
        self.multi_fill_check.setToolTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        multi_layout.addWidget(self.multi_fill_check, 0, 1)

        # Whether to save the PDF as form-fillable still
        multi_design_label = QLabel("Use 2-Page Design:")
        multi_design_label.setToolTip("Chooses whether to use the single card or two page card designs for output.")
        multi_layout.addWidget(multi_design_label, 1, 0)
        self.multi_design_check = QCheckBox()
        self.multi_design_check.setToolTip("Chooses whether to use the single card or two page card designs for output.")
        multi_layout.addWidget(self.multi_design_check, 1, 1)

        # PDF Output Name
        self.numgun_line_edit = add_stat_to_layout(multi_layout, "# Guns to Generate:", 2, force_int=True)
        self.numgun_line_edit.setToolTip("Choose how many guns to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Guns")
        button.setToolTip("Handles generating the guns and locally saving their PDFs in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_multiple_guns())
        multi_layout.addWidget(button, 3, 0, 1, -1)

        # Label for savefile output
        self.multi_output_label = QLabel()
        multi_layout.addWidget(self.multi_output_label, 4, 0, 1, -1)

        # Grid layout
        multi_group.setLayout(multi_layout)
        ###################################
        ###  END: Multi Generation      ###
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
        self.current_pdf = "EXAMPLE_GUN.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/guns/EXAMPLE_GUN.pdf")).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        gun_card_group.setLayout(gun_card_layout)
        ###################################
        ###  END: Gun Display           ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(300)
        generation_group.setFixedWidth(300)
        multi_group.setFixedWidth(300)
        gun_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(300)
        generation_group.setFixedHeight(150)
        multi_group.setFixedHeight(350)
        gun_card_group.setFixedHeight(800)

        # Gun Generation Layout
        self.gun_generation_layout = QGridLayout()
        self.gun_generation_layout.addWidget(base_stats_group, 0, 0)
        self.gun_generation_layout.addWidget(generation_group, 1, 0)
        self.gun_generation_layout.addWidget(multi_group, 2, 0)
        self.gun_generation_layout.addWidget(gun_card_group, 0, 1, -1, 1)

        self.gun_tab = QWidget()
        self.gun_tab.setLayout(self.gun_generation_layout)

    def get_tab(self):
        return self.gun_tab

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
        prefix = self.prefix_box.currentText()
        if ']' in prefix:
            prefix = prefix[1:prefix.index("]")]

        redtext = self.redtext_box.currentText()
        if ']' in redtext:
            redtext = redtext[1:redtext.index("]")].split('-')[0]

        redtext_check = self.hide_redtext_check.isChecked()
        color_check = self.rarity_border_check.isChecked()
        form_check = self.form_fill_check.isChecked()

        # Get the gun balance type
        damage_balance_json = self.gun_balance_dict[self.gun_balance_box.currentText()]

        # Generate the gun object
        gun = Gun(self.basedir, name=name, item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                  damage_balance=damage_balance_json, rarity_element=element_roll, prefix=prefix, redtext=redtext)

        # Generate the PDF output name as the gun name
        output_name = f"{gun.type.title().replace('_', ' ')}_{gun.rarity.title()}_{gun.guild.title()}_{gun.name}".replace(' ', '') \
            if self.pdf_line_edit.text() == "" else self.pdf_line_edit.text()

        # Check if it is already in use
        if output_name == self.current_pdf:
            self.output_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        self.output_pdf_label.setText("Saved to output/guns/{}.pdf!".format(output_name))
        self.current_pdf = output_name

        # Generate the local gun card PDF depending on the form design chosen
        if self.form_design_check.isChecked():
            self.gun_pdf.generate_split_gun_pdf(output_name, gun, self.gun_images, color_check, form_check, redtext_check)
        else:
            self.gun_pdf.generate_gun_pdf(output_name, gun, self.gun_images, color_check, form_check, redtext_check)

        # Load in gun card PDF
        f = Path(os.path.abspath("output/guns/{}.pdf".format(output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_guns(self):
        """ Handles performing the call to automatically generate multiple guns and save them to outputs  """
        # Check for set constants
        item_level = self.item_level_box.currentText().lower()

        gun_type = self.gun_type_box.currentText().lower().replace(' ', '_')    # Convert gun type to digit
        if gun_type != "random":
            gun_type = str(self.gun_type_choices.index(gun_type) + 1)

        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_roll = self.element_roll.isChecked()

        # Error check for no number specified
        if self.numgun_line_edit.text() == "":
            self.multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Check for rarity and prefix checks
        prefix = self.prefix_box.currentText()
        if ']' in prefix:
            prefix = prefix[1:prefix.index("]")]

        redtext = self.redtext_box.currentText()
        if ']' in redtext:
            redtext = redtext[1:redtext.index("]")].split('-')[0]

        redtext_check = self.hide_redtext_check.isChecked()
        color_check = self.rarity_border_check.isChecked()
        form_check = self.form_fill_check.isChecked()

        # Get the gun balance type
        damage_balance_json = self.gun_balance_dict[self.gun_balance_box.currentText()]

        # Get a base output name to display and the number to generate
        output_name = "EXAMPLE"
        number_gen = int(self.numgun_line_edit.text())

        # Generate N guns
        for _ in range(number_gen):
            # Generate the gun object
            gun = Gun(self.basedir, item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                      damage_balance=damage_balance_json, rarity_element=element_roll, prefix=prefix, redtext=redtext)

            # Generate the PDF output name as the gun name
            output_name = f"{gun.type.title().replace('_', ' ')}_{gun.rarity.title()}_{gun.guild.title()}_{gun.name}".replace(' ', '')

            # Check if it is already in use
            if output_name == self.current_pdf:
                self.multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the local gun card PDF
            if self.multi_design_check.isChecked():
                self.gun_pdf.generate_split_gun_pdf(output_name, gun, self.gun_images, color_check, form_check, redtext_check)
            else:
                self.gun_pdf.generate_gun_pdf(output_name, gun, self.gun_images, color_check, form_check, redtext_check)

        # Set text and current PDF name
        self.multi_output_label.setText("Saved {} guns to 'output/guns/'!".format(number_gen))
        self.current_pdf = output_name

        # Load in last generated gun card PDF
        f = Path(os.path.abspath("output/guns/{}.pdf".format(output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)
