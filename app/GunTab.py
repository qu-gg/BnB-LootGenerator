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

from app.tab_utils import add_stat_to_layout, copy_image_action, save_image_action, update_config
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QAxContainer, QtCore, QtWidgets
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton,
                             QCheckBox, QFileDialog, QLineEdit)


class GunTab(QWidget):
    def __init__(self, basedir, statusbar, config, foundry_translator):
        super(GunTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.gun_images = GunImage(self.basedir)
        self.gun_pdf = GunPDF(self.basedir, self.statusbar, self.gun_images)

        # Config
        self.config = config

        # API Classes
        self.foundry_translator = foundry_translator

        ###################################
        ###  BEGIN: Base Stats Grid     ###
        ###################################
        base_stats_group = QGroupBox("Configuration")
        base_stats_layout = QGridLayout()
        base_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ##### Information Separator
        information_separator = QLabel("Gun Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Gun Name
        self.name_line_edit = add_stat_to_layout(base_stats_layout, "Gun Name:", idx)
        idx += 1

        # Item Level
        base_stats_layout.addWidget(QLabel("Item Level: "), idx, 0)
        self.item_level_box = QComboBox()
        self.item_level_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/gun_types.json").get("pistol").keys():
            self.item_level_box.addItem(item)
        base_stats_layout.addWidget(self.item_level_box, idx, 1)
        idx += 1

        # Gun Type
        self.gun_type_choices = list(get_file_data(basedir + "resources/guns/gun_types.json").keys())
        base_stats_layout.addWidget(QLabel("Gun Type: "), idx, 0)
        self.gun_type_box = QComboBox()
        self.gun_type_box.addItem("Random")
        for item in self.gun_type_choices:
            self.gun_type_box.addItem(item.capitalize().replace('_', ' '))
        base_stats_layout.addWidget(self.gun_type_box, idx, 1)
        idx += 1

        # Guild
        base_stats_layout.addWidget(QLabel("Guild: "), idx, 0)
        self.guild_type_box = QComboBox()
        self.guild_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/guild_table.json").keys():
            self.guild_type_box.addItem(item.capitalize())
        base_stats_layout.addWidget(self.guild_type_box, idx, 1)
        idx += 1

        # Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
        base_stats_layout.addWidget(QLabel("Rarity: "), idx, 0)
        self.rarity_type_box = QComboBox()
        for item in rarities:
            self.rarity_type_box.addItem(item)
        base_stats_layout.addWidget(self.rarity_type_box, idx, 1)
        idx += 1

        # Prefix: [None, Random, Selection]
        base_stats_layout.addWidget(QLabel("Prefix: "), idx, 0)
        self.prefix_box = QComboBox()
        self.prefix_box.addItem("None")
        self.prefix_box.addItem("Random")
        for pidx, (key, item) in enumerate(get_file_data(basedir + "resources/guns/prefix.json").items()):
            self.prefix_box.addItem(f"[{pidx + 1}] {item['name']}")
        self.prefix_box.setStatusTip("Choose whether to add a random Prefix or a specific one")
        base_stats_layout.addWidget(self.prefix_box, idx, 1)
        idx += 1

        # RedText: [None, Random, Selection]
        base_stats_layout.addWidget(QLabel("Red Text: "), idx, 0)
        self.redtext_box = QComboBox()
        self.redtext_box.addItem("None")
        self.redtext_box.addItem("Random (All Rarities)")
        self.redtext_box.addItem("Random (Epics+)")
        self.redtext_box.addItem("Random (Legendaries)")
        for key, item in get_file_data(basedir + "resources/guns/redtext.json").items():
            self.redtext_box.addItem(f"[{key}] {item['name']}")

        self.redtext_box.setCurrentIndex(3)
        self.redtext_box.setStatusTip("Choose whether to add a random RedText for Epics/Legendaries or a specific one regardless of rarity")
        base_stats_layout.addWidget(self.redtext_box, idx, 1)
        idx += 1

        # Whether to hide Red Text Effects
        hide_redtext_label = QLabel("Hide Red Text Effect: ")
        hide_redtext_label.setStatusTip("Whether to show the text but high the effect for Red Texts")
        base_stats_layout.addWidget(hide_redtext_label, idx, 0)
        self.hide_redtext_check = QCheckBox()
        self.hide_redtext_check.setStatusTip("Whether to show the text but high the effect for Red Texts")
        base_stats_layout.addWidget(self.hide_redtext_check, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Element Separator
        element_separator = QLabel("Element Selection")
        element_separator.setFont(font)
        element_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(element_separator, idx, 0, 1, -1)
        idx += 1

        # Forcing specific elements to be present
        element_icon_paths = {
            "cryo": "Cryo.png",
            "corrosive": "Corrosion.png",
            "explosive": "Explosive.png",
            "incendiary": "Incendiary.png",
            "radiation": "Radiation.png",
            "shock": "Shock.png"
        }

        # Build a dictionary of button object IDs
        self.element_checkboxes = dict()
        element_buttons = QGridLayout()
        for i, icon in enumerate(element_icon_paths.keys()):
            element_checkbox = QCheckBox()
            element_checkbox.setIcon(QIcon(f"resources/images/element_icons/{element_icon_paths[icon]}"))
            element_checkbox.setStatusTip(f"Choose whether the {icon.title()} element is always added.")

            if i < len(element_icon_paths.keys()) // 2:
                element_buttons.addWidget(element_checkbox, 0, i)
            else:
                element_buttons.addWidget(element_checkbox, 1, i % 3)
            self.element_checkboxes[icon] = element_checkbox

        base_stats_layout.addWidget(QLabel("Select Specific Elements:"), idx, 0, QtCore.Qt.AlignTop)
        base_stats_layout.addLayout(element_buttons, idx, 1, QtCore.Qt.AlignTop)
        idx += 2

        # Setting a custom element damage die
        self.element_damage_die_edit = add_stat_to_layout(base_stats_layout, "Custom Element Damage:", idx, placeholder='e.g. 1d8')
        self.element_damage_die_edit.setStatusTip("Choose a specific damage die (e.g. 1d20) to replace the elemental damage bonus.")
        idx += 1

        # Whether to force an element roll on the table
        element_roll_text_label = QLabel("Force an Element Roll: ")
        element_roll_text_label.setStatusTip(
            "Choose whether to always add an element roll regardless of the rarity rolled. "
            "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(element_roll_text_label, idx, 0)
        self.element_roll = QCheckBox()
        self.element_roll.setStatusTip(
            "Choose whether to always add an element roll regardless of the rarity rolled. "
            "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(self.element_roll, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
        idx += 1

        # Filepath display for custom art
        self.art_filepath = QLineEdit("")

        # Buttons and file dialog associated with selecting local files
        art_gridlayout = QGridLayout()
        self.art_filedialog = QFileDialog()
        self.art_filedialog.setStatusTip("Uses custom art on the gun art side when given either a local image path or a URL.")

        self.art_select = QPushButton("Open")
        self.art_select.clicked.connect(self.open_file)
        self.art_select.setStatusTip("Used to select an image to use in place of the Borderlands gun art.")

        art_gridlayout.addWidget(self.art_filepath, 0, 1)
        art_gridlayout.addWidget(self.art_select, 0, 2)

        base_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        base_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Whether to show rarity-based color splashes behind the gun
        rarity_border_label = QLabel("Use Gun Color Splashes: ")
        rarity_border_label.setStatusTip("Choose whether to outline the gun art in a colored-outline based on rarity.")
        base_stats_layout.addWidget(rarity_border_label, idx, 0)
        self.rarity_border_check = QCheckBox()
        self.rarity_border_check.setStatusTip("Choose whether to outline the gun art in a colored-outline based on rarity.")
        base_stats_layout.addWidget(self.rarity_border_check, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Rules/Misc Separator
        rules_separator = QLabel("Rules/Settings")
        rules_separator.setFont(font)
        rules_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(rules_separator, idx, 0, 1, -1)
        idx += 1

        # Gun Balance Table
        self.gun_balance_dict = {
            "Source Book": 'gun_types',
            "McCoby\'s": "gun_types_mccoby",
            "RobMWJ\'s": "gun_types_robmwj"
        }
        balance_label = QLabel("Damage Balance Sheet: ")
        balance_label.setStatusTip("Choose which Gun Damage Balance system to use - either the source book\'s or homebrew alternatives.")
        base_stats_layout.addWidget(balance_label, idx, 0)
        self.gun_balance_box = QComboBox()
        for item in self.gun_balance_dict.keys():
            self.gun_balance_box.addItem(item)
        self.gun_balance_box.setStatusTip("Choose whether to use non-base gun balance sheets, given by community members.")
        base_stats_layout.addWidget(self.gun_balance_box, idx, 1)
        idx += 1

        # Whether to save the PDF as form-fillable still
        form_fill_label = QLabel("Keep PDF Form-Fillable:")
        form_fill_label.setStatusTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        base_stats_layout.addWidget(form_fill_label, idx, 0)
        self.form_fill_check = QCheckBox()
        self.form_fill_check.setStatusTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        base_stats_layout.addWidget(self.form_fill_check, idx, 1)
        idx += 1

        # Whether to use the single page or 2-page PDF design
        form_design_label = QLabel("Use 2-Page Design:")
        form_design_label.setStatusTip("Chooses whether to use the single card or two page card designs for output.")
        base_stats_layout.addWidget(form_design_label, idx, 0)
        self.form_design_check = QCheckBox()
        self.form_design_check.setStatusTip(
            "Chooses whether to use the single card or two page card designs for output.")
        base_stats_layout.addWidget(self.form_design_check, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### APIs
        apis_separator = QLabel("External Tools")
        apis_separator.setFont(font)
        apis_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(apis_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        base_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        base_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

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

        # PDF Output Name
        self.pdf_line_edit = add_stat_to_layout(generation_layout, "PDF Filename:", 0)
        self.pdf_line_edit.setStatusTip("Specify the filename that Generate Gun saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Gun")
        button.setStatusTip("Handles generating the gun and locally saving the PDF in \"outputs/\".")
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
        ###  START: Multi Generation    ###
        ###################################
        multi_group = QGroupBox("Multi-Gun Generation")
        multi_layout = QGridLayout()
        multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numgun_line_edit = add_stat_to_layout(multi_layout, "# Guns to Generate:", 0, force_int=True)
        self.numgun_line_edit.setStatusTip("Choose how many guns to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Guns")
        button.setStatusTip("Handles generating the guns and locally saving their PDFs in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_multiple_guns())
        multi_layout.addWidget(button, 1, 0, 1, -1)

        # Grid layout
        multi_group.setLayout(multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Gun Display         ###
        ###################################
        self.gun_card_group = QGroupBox("Gun Card")
        gun_card_layout = QGridLayout()
        gun_card_layout.setAlignment(Qt.AlignVCenter)

        self.WebBrowser = QAxContainer.QAxWidget(self)
        self.WebBrowser.setFixedHeight(800)
        self.WebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.WebBrowser.setStatusTip("If nothing is displaying or the text is not displaying, then either "
                                   "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        gun_card_layout.addWidget(self.WebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_pdf = "EXAMPLE_GUN.pdf"
        self.output_name = ""

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/examples/EXAMPLE_GUN.pdf")).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Give a right-click menu for copying image cards
        self.display_height = 660
        self.gun_card_group.setContextMenuPolicy(Qt.ActionsContextMenu)

        # Enable copy-pasting image cards
        self.gun_card_group.addAction(
            copy_image_action(self, self.gun_card_group.winId(), height=self.display_height, y=100))

        # Enable copy-pasting image cards
        self.gun_card_group.addAction(
            save_image_action(self, self.gun_card_group.winId(), image_type="guns", height=self.display_height, y=100))

        # Grid layout
        self.gun_card_group.setLayout(gun_card_layout)
        ###################################
        ###  END: Gun Display           ###
        ###################################

        ###################################
        ###  START: Configuration       ###
        ###################################
        self.hide_redtext_check.setChecked(self.config['gun_tab']['hide_red_text'])
        self.hide_redtext_check.clicked.connect(
            lambda: update_config(basedir, self.hide_redtext_check, self.config, 'gun_tab', 'hide_red_text'))

        self.rarity_border_check.setChecked(self.config['gun_tab']['use_color_splashes'])
        self.rarity_border_check.clicked.connect(
            lambda: update_config(basedir, self.rarity_border_check, self.config, 'gun_tab', 'use_color_splashes'))

        self.form_fill_check.setChecked(self.config['gun_tab']['pdf_form_fillable'])
        self.form_fill_check.clicked.connect(
            lambda: update_config(basedir, self.form_fill_check, self.config, 'gun_tab', 'pdf_form_fillable'))

        self.form_design_check.setChecked(self.config['gun_tab']['pdf_two_page_design'])
        self.form_design_check.clicked.connect(
            lambda: update_config(basedir, self.form_design_check, self.config, 'gun_tab', 'pdf_two_page_design'))

        self.foundry_export_check.setChecked(self.config['gun_tab']['foundry_export'])
        self.foundry_export_check.clicked.connect(
            lambda: update_config(basedir, self.foundry_export_check, self.config, 'gun_tab', 'foundry_export'))
        ###################################
        ###  END: Configuration         ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(300)
        generation_group.setFixedWidth(300)
        multi_group.setFixedWidth(300)
        self.gun_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(630)
        generation_group.setFixedHeight(110)
        multi_group.setFixedHeight(110)
        self.gun_card_group.setFixedHeight(850)

        # Gun Generation Layout
        self.gun_generation_layout = QGridLayout()
        self.gun_generation_layout.addWidget(base_stats_group, 0, 0)
        self.gun_generation_layout.addWidget(generation_group, 1, 0)
        self.gun_generation_layout.addWidget(multi_group, 2, 0)
        self.gun_generation_layout.addWidget(self.gun_card_group, 0, 1, -1, 1)

        self.gun_tab = QWidget()
        self.gun_tab.setLayout(self.gun_generation_layout)

    def get_tab(self):
        return self.gun_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def save_screenshot(self):
        """ Screenshots the Gun Card layout and saves to a local file """
        # Save as local image
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.gun_card_group.winId(), height=self.display_height, y=100)
        screenshot.save(f"output/guns/{self.output_name}.png", "png")

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

        element_damage = self.element_damage_die_edit.text()
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

        art_filepath = self.art_filepath.text()

        # Get the gun balance type
        damage_balance_json = self.gun_balance_dict[self.gun_balance_box.currentText()]

        # Build list of elements that are manually selected
        selected_elements = []
        for element_key in self.element_checkboxes.keys():
            if self.element_checkboxes[element_key].isChecked():
                selected_elements.append(element_key)

        # Generate the gun object
        gun = Gun(self.basedir, self.gun_images,
                  name=name, item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                  damage_balance=damage_balance_json,
                  element_damage=element_damage, rarity_element=element_roll, selected_elements=selected_elements,
                  prefix=prefix, redtext=redtext,
                  gun_art=art_filepath)

        # Generate the PDF output name as the gun name
        self.output_name = f"{gun.type.title().replace('_', ' ')}_Level{int(gun.item_level.split('-')[0])}_{gun.rarity.title()}_{gun.guild.title()}_{gun.name}".replace(' ', '') \
            if self.pdf_line_edit.text() == "" else self.pdf_line_edit.text()

        # Check if it is already in use
        if self.output_name == self.current_pdf:
            self.output_pdf_label.setText("PDF Name already in use!".format(self.output_name))
            return

        self.output_pdf_label.setText("Saved to output/guns/{}.pdf!".format(self.output_name))
        self.current_pdf = self.output_name

        # Generate the local gun card PDF depending on the form design chosen
        if self.form_design_check.isChecked():
            self.gun_pdf.generate_split_gun_pdf(self.output_name, gun, color_check, form_check, redtext_check)
        else:
            self.gun_pdf.generate_gun_pdf(self.output_name, gun, color_check, form_check, redtext_check)

        # Load in gun card PDF
        f = Path(os.path.abspath("output/guns/{}.pdf".format(self.output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_gun(gun, self.output_name, redtext_check)

    def generate_multiple_guns(self):
        """ Handles performing the call to automatically generate multiple guns and save them to outputs  """
        # Check for set constants
        item_level = self.item_level_box.currentText().lower()

        gun_type = self.gun_type_box.currentText().lower().replace(' ', '_')    # Convert gun type to digit
        if gun_type != "random":
            gun_type = str(self.gun_type_choices.index(gun_type) + 1)

        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_damage = self.element_damage_die_edit.text()
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

        art_filepath = self.art_filepath.text()

        # Get the gun balance type
        damage_balance_json = self.gun_balance_dict[self.gun_balance_box.currentText()]

        # Get a base output name to display and the number to generate
        self.output_name = "EXAMPLE"
        number_gen = int(self.numgun_line_edit.text())

        # Build list of elements that are manually selected
        selected_elements = []
        for element_key in self.element_checkboxes.keys():
            if self.element_checkboxes[element_key].isChecked():
                selected_elements.append(element_key)

        # Generate N guns
        for _ in range(number_gen):
            # Generate the gun object
            gun = Gun(self.basedir, self.gun_images,
                      item_level=item_level, gun_type=gun_type, gun_guild=guild, gun_rarity=rarity,
                      damage_balance=damage_balance_json,
                      element_damage=element_damage, rarity_element=element_roll, selected_elements=selected_elements,
                      prefix=prefix, redtext=redtext,
                      gun_art=art_filepath)

            # Generate the PDF output name as the gun name
            self.output_name = f"{gun.type.title().replace('_', ' ')}_Level{int(gun.item_level.split('-')[0])}_{gun.rarity.title()}_{gun.guild.title()}_{gun.name}".replace(' ', '')

            # Check if it is already in use
            if self.output_name == self.current_pdf:
                self.multi_output_label.setText("PDF Name already in use!".format(self.output_name))
                continue

            # Generate the local gun card PDF
            if self.form_design_check.isChecked():
                self.gun_pdf.generate_split_gun_pdf(self.output_name, gun, color_check, form_check, redtext_check)
            else:
                self.gun_pdf.generate_gun_pdf(self.output_name, gun, color_check, form_check, redtext_check)

            # FoundryVTT Check
            if self.foundry_export_check.isChecked() is True:
                self.foundry_translator.export_gun(gun, self.output_name, redtext_check)

        # Set text and current PDF name
        self.multi_output_label.setText("Saved {} guns to 'output/guns/'!".format(number_gen))
        self.current_pdf = self.output_name

        # Load in last generated gun card PDF
        f = Path(os.path.abspath("output/guns/{}.pdf".format(self.output_name))).as_uri()
        self.WebBrowser.dynamicCall('Navigate(const QString&)', f)
