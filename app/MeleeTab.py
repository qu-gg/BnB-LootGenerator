"""
@file MeleeTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to melee generation
"""
from classes.GunImage import GunImage
from classes.MeleeWeapon import MeleeWeapon

from app.tab_utils import add_stat_to_layout, copy_image_action, save_image_action
from classes.json_reader import get_file_data

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QKeySequence, QClipboard, QGuiApplication
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton,
                             QCheckBox, QFileDialog, QLineEdit, QTextEdit, QShortcut, QAction)


class MeleeTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(MeleeTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.melee_images = GunImage(self.basedir)

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
        information_separator = QLabel("Melee Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Melee Name
        self.name_line_edit = add_stat_to_layout(base_stats_layout, "Melee Name:", idx)
        idx += 1

        # Item Level
        base_stats_layout.addWidget(QLabel("Item Level: "), idx, 0)
        self.item_level_box = QComboBox()
        self.item_level_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/gun_types.json").get("pistol").keys():
            self.item_level_box.addItem(item)
        base_stats_layout.addWidget(self.item_level_box, idx, 1)
        idx += 1

        # Guild
        base_stats_layout.addWidget(QLabel("Guild: "), idx, 0)
        self.guild_type_box = QComboBox()
        self.guild_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/melees/guild_table.json").keys():
            self.guild_type_box.addItem(item.title())
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
        self.prefix_box.addItem("Random")
        for pidx, (key, item) in enumerate(get_file_data(basedir + "resources/misc/melees/prefix.json").items()):
            if item['name'] == "":
                self.prefix_box.addItem(f"[{key}] None")
            else:
                self.prefix_box.addItem(f"[{key}] {item['name']}")
        self.prefix_box.setStatusTip("Choose whether to add a random Prefix or a specific one")
        base_stats_layout.addWidget(self.prefix_box, idx, 1)
        idx += 1

        # Redtext Name
        self.redtext_line_edit = add_stat_to_layout(base_stats_layout, "RedText: ", idx)
        self.redtext_line_edit.setStatusTip("")
        idx += 1

        # Redtext Effect
        self.redtext_effect_line_edit = add_stat_to_layout(base_stats_layout, "RedText Effect: ", idx)
        self.redtext_effect_line_edit.setStatusTip("")
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
        self.element_icon_paths = {
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
        for i, icon in enumerate(self.element_icon_paths.keys()):
            element_checkbox = QCheckBox()
            element_checkbox.setIcon(QIcon(f"resources/images/element_icons/{self.element_icon_paths[icon]}"))
            element_checkbox.setStatusTip(f"Choose whether the {icon.title()} element is always added.")

            if i < len(self.element_icon_paths.keys()) // 2:
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
        self.art_filedialog.setStatusTip("Uses custom art on the melee art side when given either a local image path or a URL.")

        self.art_select = QPushButton("Open")
        self.art_select.clicked.connect(self.open_file)
        self.art_select.setStatusTip("Used to select an image to use in place of the Borderlands melee art.")

        art_gridlayout.addWidget(self.art_filepath, 0, 1)
        art_gridlayout.addWidget(self.art_select, 0, 2)

        base_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        base_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Grid layout
        base_stats_group.setLayout(base_stats_layout)
        ###################################
        ###  END: Base Stats Grid       ###
        ###################################

        ###################################
        ###  START: Generation          ###
        ###################################
        generation_group = QGroupBox("Single-Melee Generation")
        generation_layout = QGridLayout()
        generation_layout.setAlignment(Qt.AlignTop)

        # Generate button
        button = QPushButton("Generate Melee")
        button.setStatusTip("Handles generating the melee.")
        button.clicked.connect(lambda: self.generate_melee())
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
        ###  START: Melee Display       ###
        ###################################
        self.melee_card_group = QGroupBox("Melee Card")
        self.melee_card_layout = QGridLayout()
        self.melee_card_layout.setAlignment(Qt.AlignTop)

        # Give a right-click menu for copying image cards
        self.display_height = 750
        self.melee_card_group.setContextMenuPolicy(Qt.ActionsContextMenu)

        # Enable copy-pasting image cards
        self.melee_card_group.addAction(
            copy_image_action(self, self.melee_card_group.winId(), height=self.display_height))

        # Enable saving image cards
        self.melee_card_group.addAction(
            save_image_action(self, self.melee_card_group.winId(), image_type="melees", height=self.display_height))

        self.melee_card_group.setLayout(self.melee_card_layout)
        ###################################
        ###  END: Melee Display         ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(300)
        generation_group.setFixedWidth(300)
        self.melee_card_group.setFixedWidth(325)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(450)
        generation_group.setFixedHeight(400)
        self.melee_card_group.setFixedHeight(850)

        # melee Generation Layout
        self.melee_generation_layout = QGridLayout()
        self.melee_generation_layout.setAlignment(Qt.AlignLeft)
        self.melee_generation_layout.addWidget(base_stats_group, 0, 0)
        self.melee_generation_layout.addWidget(generation_group, 1, 0)
        self.melee_generation_layout.addWidget(self.melee_card_group, 0, 1, -1, 1)

        self.melee_tab = QWidget()
        self.melee_tab.setLayout(self.melee_generation_layout)

    def get_tab(self):
        return self.melee_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def clear_layout(self, layout):
        """
        Wipe the current melee card. Technically has a memory leak on the 'wiped' components, but
        really a non-issue with how much memory it would accumulate.
        :param layout: QtLayout of the Melee Card
        """
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def split_effect_text(self, initial_string, line_length=32):
        """
        Handles splitting an effect string into multiple lines depending on the length of words.
        Cleaner for visualizing in the cards
        :param initial_string: effect string to split
        :param line_length: length of line to split
        :return: line with newlines put in
        """
        cur_chars = 0
        info = ""
        for idx, word in enumerate(initial_string.split(" ")):
            cur_chars += len(word)
            if cur_chars > line_length:
                info += "\n"
                cur_chars = len(word)

            info += f"{word} "
        return info

    def save_screenshot(self):
        """ Screenshots the Melee Card layout and saves to a local file """
        # Save as local image
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.melee_card_group.winId(), height=self.display_height)
        screenshot.save(f"output/melees/{self.output_name}.png", "png")

        # Set label text for output
        self.output_pdf_label.setText(f"Saved to output/melees/{self.output_name}.png")

    def generate_melee(self):
        """
        Handles performing the call to generate a Melee Weapon given the
        parameters and updating the Melee Card image
        """
        # Load in properties that are currently set in the program
        name = None if self.name_line_edit.text() == "" else self.name_line_edit.text()
        item_level = self.item_level_box.currentText().lower()
        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_damage = self.element_damage_die_edit.text()
        element_roll = self.element_roll.isChecked()

        prefix = self.prefix_box.currentText()
        if ']' in prefix:
            prefix = prefix[1:prefix.index("]")]

        redtext_name = self.redtext_line_edit.text()
        redtext_info = self.redtext_effect_line_edit.text()

        art_filepath = self.art_filepath.text()

        # Build list of elements that are manually selected
        selected_elements = []
        for element_key in self.element_checkboxes.keys():
            if self.element_checkboxes[element_key].isChecked():
                selected_elements.append(element_key)

        # Generate the melee object
        melee = MeleeWeapon(self.basedir, self.melee_images,
                  name=name, item_level=item_level, melee_guild=guild, melee_rarity=rarity,
                  element_damage=element_damage, rarity_element=element_roll, selected_elements=selected_elements,
                  prefix=prefix, redtext_name=redtext_name, redtext_info=redtext_info, melee_art=art_filepath)

        # Clear current melee card
        self.clear_layout(self.melee_card_layout)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Pixmap for the MeleeWeapon Image
        melee_display = QLabel()
        melee_pixmap = QPixmap(melee.melee_art_path).scaled(300, 300, Qt.KeepAspectRatio,
                                                            transformMode=QtCore.Qt.SmoothTransformation)
        melee_display.setAlignment(Qt.AlignCenter)
        melee_display.setPixmap(melee_pixmap)
        self.melee_card_layout.addWidget(melee_display, idx, 0, 1, -1)
        idx += 1

        # Add spacing between groups
        self.melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Melee Weapon Name
        melee_name = add_stat_to_layout(self.melee_card_layout, "Name: ", idx)
        melee_name.setText(melee.name)
        idx += 1

        # Melee Weapon Item Level
        melee_item_level = add_stat_to_layout(self.melee_card_layout, "Item Level: ", idx)
        melee_item_level.setText(melee.item_level)
        idx += 1

        # Melee Weapon Item Level
        melee_rarity = add_stat_to_layout(self.melee_card_layout, "Rarity: ", idx)
        melee_rarity.setText(melee.rarity.title())
        idx += 1

        # Melee Weapon Guild Name
        melee_guild = add_stat_to_layout(self.melee_card_layout, "Guild: ", idx)
        melee_guild.setText(melee.guild.title())
        idx += 1

        # Melee Guild effect, dynamically expanded
        melee_guild_effect = QTextEdit()
        prefix_info = self.split_effect_text(melee.guild_mod)
        numOfLinesInText = prefix_info.count("\n") + 2
        melee_guild_effect.setFixedHeight(numOfLinesInText * 15)
        melee_guild_effect.setFixedWidth(220)
        melee_guild_effect.setText(prefix_info)

        self.melee_card_layout.addWidget(QLabel("Guild Effect: "), idx, 0, numOfLinesInText, 1)
        self.melee_card_layout.addWidget(melee_guild_effect, idx, 1, numOfLinesInText, 1)
        idx += numOfLinesInText

        # Add spacing between groups
        self.melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Melee Weapon Prefix
        melee_prefix = add_stat_to_layout(self.melee_card_layout, "Prefix: ", idx)
        melee_prefix.setText(melee.prefix_name)
        idx += 1

        # Melee Weapon Prefix Info
        if melee.prefix_name != "":
            # If the prefix has information, make it a multi-line TextEdit
            melee_prefix_effect = QTextEdit()
            prefix_info = self.split_effect_text(melee.prefix_info)
            numOfLinesInText = prefix_info.count("\n") + 2
            melee_prefix_effect.setFixedHeight(numOfLinesInText * 15)
            melee_prefix_effect.setFixedWidth(220)
            melee_prefix_effect.setText(prefix_info)

            self.melee_card_layout.addWidget(QLabel("Prefix Effect: "), idx, 0, numOfLinesInText, 1)
            self.melee_card_layout.addWidget(melee_prefix_effect, idx, 1, numOfLinesInText, 1)
            idx += numOfLinesInText
        else:
            # Otherwise just make it a blank TextEdit with fixed height and number of lienes
            numOfLinesInText = 4

            melee_prefix_effect = QTextEdit()
            melee_prefix_effect.setText("")
            melee_prefix_effect.setFixedHeight(numOfLinesInText * 15)
            melee_prefix_effect.setFixedWidth(220)

            self.melee_card_layout.addWidget(QLabel("Prefix Effect: "), idx, 0, numOfLinesInText, 1)
            self.melee_card_layout.addWidget(melee_prefix_effect, idx, 1, numOfLinesInText, 1)
            idx += numOfLinesInText

        # Add spacing between groups
        self.melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Melee Weapon RedText
        melee_redtext_name = add_stat_to_layout(self.melee_card_layout, "RedText Name: ", idx)
        melee_redtext_name.setText(melee.redtext_name)
        idx += 1

        # Melee Weapon RedText Information
        if melee.redtext_name != "":
            # If the redtext has information, make it a multi-line TextEdit
            melee_redtext_effect = QTextEdit()
            prefix_info = self.split_effect_text(melee.redtext_info)
            numOfLinesInText = prefix_info.count("\n") + 2
            melee_redtext_effect.setFixedHeight(numOfLinesInText * 15)
            melee_redtext_effect.setFixedWidth(220)
            melee_redtext_effect.setText(prefix_info)

            self.melee_card_layout.addWidget(QLabel("RedText Effect: "), idx, 0, numOfLinesInText, 1)
            self.melee_card_layout.addWidget(melee_redtext_effect, idx, 1, numOfLinesInText, 1)
            idx += numOfLinesInText
        else:
            # Otherwise just make it a blank TextEdit with fixed height and number of lines
            numOfLinesInText = 4

            melee_redtext_effect = QTextEdit()
            melee_redtext_effect.setText("")
            melee_redtext_effect.setFixedHeight(numOfLinesInText * 15)
            melee_redtext_effect.setFixedWidth(220)

            self.melee_card_layout.addWidget(QLabel("RedText Effect: "), idx, 0, numOfLinesInText, 1)
            self.melee_card_layout.addWidget(melee_redtext_effect, idx, 1, numOfLinesInText, 1)
            idx += numOfLinesInText

        # Add spacing between groups
        self.melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Build a dictionary of button object IDs
        melee_element_checkboxes = dict()
        melee_elements = QGridLayout()
        melee_elements.setAlignment(Qt.AlignCenter)
        for i, icon in enumerate(self.element_icon_paths.keys()):
            element_checkbox = QCheckBox()
            element_checkbox.setIcon(QIcon(f"resources/images/element_icons/{self.element_icon_paths[icon]}"))

            if i < len(self.element_icon_paths.keys()) // 2:
                melee_elements.addWidget(element_checkbox, 0, i)
            else:
                melee_elements.addWidget(element_checkbox, 1, i % 3)
            melee_element_checkboxes[icon] = element_checkbox

        self.melee_card_layout.addWidget(QLabel("Elements:"), idx, 0, QtCore.Qt.AlignTop)
        self.melee_card_layout.addLayout(melee_elements, idx, 1, QtCore.Qt.AlignTop)
        idx += 2

        # Set elements to checked
        for element in melee_element_checkboxes.keys():
            if element in melee.element:
                melee_element_checkboxes[element].setChecked(True)

        # Melee Weapon Guild
        melee_element_damage = add_stat_to_layout(self.melee_card_layout, "Element Die: ", idx)
        melee_element_damage.setText(melee.element_bonus)
        idx += 1

        # Save as output
        self.output_name = f"Level{int(melee.item_level.split('-')[0])}_{melee.guild.title()}_" \
                           f"{melee.rarity.title()}_{melee.name}".replace(' ', '')
        QTimer.singleShot(1000, self.save_screenshot)
