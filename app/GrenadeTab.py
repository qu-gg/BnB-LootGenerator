"""
@file GrenadeTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to grenade generation
"""
import os
from pathlib import Path

from PyQt5.QtGui import QFont

from classes.Grenade import Grenade
from classes.GrenadePDF import GrenadePDF
from classes.GrenadeImage import GrenadeImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer, QtCore
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton, QLineEdit, QFileDialog,
                             QCheckBox)


class GrenadeTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(GrenadeTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.grenade_images = GrenadeImage(self.basedir)
        self.grenade_pdf = GrenadePDF(self.basedir, self.statusbar, self.grenade_images)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Grenade Stats Grid    ###
        ###################################
        grenade_stats_group = QGroupBox("Configuration")
        grenade_stats_layout = QGridLayout()
        grenade_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Grenade Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # grenade Name
        self.grenade_line_edit = add_stat_to_layout(grenade_stats_layout, "Grenade Name:", idx, placeholder="Random")
        idx += 1

        # grenade Guild
        grenade_stats_layout.addWidget(QLabel("Guild: "), idx, 0)
        self.guild_grenade_type_box = QComboBox()
        self.guild_grenade_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/grenades/grenade.json").keys():
            self.guild_grenade_type_box.addItem(item)
        grenade_stats_layout.addWidget(self.guild_grenade_type_box, idx, 1)
        idx += 1

        # grenade Tier
        grenade_stats_layout.addWidget(QLabel("Tier: "), idx, 0)
        self.tier_grenade_type_box = QComboBox()
        self.tier_grenade_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/grenades/grenade.json")["Ashen"].keys():
            self.tier_grenade_type_box.addItem(item)
        grenade_stats_layout.addWidget(self.tier_grenade_type_box, idx, 1)
        idx += 1

        # Grenade Type
        self.grenade_type_edit = add_stat_to_layout(grenade_stats_layout, "Type:", idx)
        self.grenade_type_edit.setToolTip("Either manually enter a grenade type or let it be rolled.")
        idx += 1

        # Grenade Damage
        self.grenade_damage_edit = add_stat_to_layout(grenade_stats_layout, "Damage:", idx, placeholder="NdX")
        self.grenade_damage_edit.setToolTip("Either manually enter a grenade damage stat or let it be rolled.")
        idx += 1

        # Grenade Effect
        self.grenade_effect_edit = add_stat_to_layout(grenade_stats_layout, "Effect:", idx)
        self.grenade_effect_edit.setToolTip("Either manually enter a grenade effect or let it be rolled.")
        idx += 1

        # Add spacing between groups
        grenade_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
        idx += 1

        # Filepath display for custom art
        self.art_filepath = QLineEdit("")

        # Buttons and file dialog associated with selecting local files
        art_gridlayout = QGridLayout()
        self.art_filedialog = QFileDialog()
        self.art_filedialog.setStatusTip(
            "Uses custom art on the relic art side when given either a local image path or a URL.")

        self.art_select = QPushButton("Open")
        self.art_select.clicked.connect(self.open_file)
        self.art_select.setStatusTip("Used to select an image to use in place of the Borderlands relic art.")

        art_gridlayout.addWidget(self.art_filepath, 0, 1)
        art_gridlayout.addWidget(self.art_select, 0, 2)

        grenade_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        grenade_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        grenade_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Rules/Misc Separator
        rules_separator = QLabel("Rules/Settings")
        rules_separator.setFont(font)
        rules_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(rules_separator, idx, 0, 1, -1)
        idx += 1

        # Whether to save the PDF as form-fillable still
        form_fill_label = QLabel("Keep PDF Form-Fillable:")
        form_fill_label.setStatusTip(
            "Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        grenade_stats_layout.addWidget(form_fill_label, idx, 0)
        self.form_fill_check = QCheckBox()
        self.form_fill_check.setStatusTip(
            "Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        grenade_stats_layout.addWidget(self.form_fill_check, idx, 1)
        idx += 1

        # Add spacing between groups
        grenade_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        grenade_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        grenade_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        grenade_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        grenade_stats_group.setLayout(grenade_stats_layout)
        ###################################
        ###  END: grenade Stats Grid      ###
        ###################################

        ###################################
        ###  START: grenade Generation    ###
        ###################################
        grenade_generation_group = QGroupBox("Single-Grenade Generation")
        grenade_generation_layout = QGridLayout()
        grenade_generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.grenade_pdf_line_edit = add_stat_to_layout(grenade_generation_layout, "PDF Filename:", 0)
        self.grenade_pdf_line_edit.setToolTip("Specify the filename that Generate grenade saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Grenade")
        button.setToolTip("Handles generating the grenade card and locally saving the PDF in \"outputs/grenades/\".")
        button.clicked.connect(lambda: self.generate_grenade())
        grenade_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for save file output
        self.output_grenade_pdf_label = QLabel()
        grenade_generation_layout.addWidget(self.output_grenade_pdf_label, 2, 0, 1, -1)

        # Grid layout
        grenade_generation_group.setLayout(grenade_generation_layout)
        ###################################
        ###  END: Grenade Generation      ###
        ###################################

        ###################################
        ###  START: Multi Generation    ###
        ###################################
        grenade_multi_group = QGroupBox("Multi-Grenade Generation")
        grenade_multi_layout = QGridLayout()
        grenade_multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numgrenade_line_edit = add_stat_to_layout(grenade_multi_layout, "# Grenades to Generate:", 0,
                                                       force_int=True)
        self.numgrenade_line_edit.setToolTip("Choose how many grenades to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Grenades")
        button.setToolTip("Handles generating the grenades and locally saving their PDFs in \"outputs/grenades/\".")
        button.clicked.connect(lambda: self.generate_multiple_grenades())
        grenade_multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.grenade_multi_output_label = QLabel()
        grenade_multi_layout.addWidget(self.grenade_multi_output_label, 2, 0, 1, -1)

        # Grid layout
        grenade_multi_group.setLayout(grenade_multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Grenade Display       ###
        ###################################
        grenade_card_group = QGroupBox("Grenade Card")
        grenade_card_layout = QGridLayout()
        grenade_card_layout.setAlignment(Qt.AlignVCenter)

        self.grenadeWebBrowser = QAxContainer.QAxWidget(self)
        self.grenadeWebBrowser.setFixedHeight(800)
        self.grenadeWebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.grenadeWebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                          "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        grenade_card_layout.addWidget(self.grenadeWebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_grenade_pdf = "EXAMPLE_GRENADE.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/examples/EXAMPLE_GRENADE.pdf")).as_uri()
        self.grenadeWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        grenade_card_group.setLayout(grenade_card_layout)
        ###################################
        ###  END: Grenade Display       ###
        ###################################

        # Setting appropriate column widths
        grenade_stats_group.setFixedWidth(300)
        grenade_generation_group.setFixedWidth(300)
        grenade_multi_group.setFixedWidth(300)
        grenade_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        grenade_stats_group.setFixedHeight(375)
        grenade_generation_group.setFixedHeight(150)
        grenade_multi_group.setFixedHeight(325)
        grenade_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.grenade_generation_layout = QGridLayout()
        self.grenade_generation_layout.addWidget(grenade_stats_group, 0, 0)
        self.grenade_generation_layout.addWidget(grenade_generation_group, 1, 0)
        self.grenade_generation_layout.addWidget(grenade_multi_group, 2, 0)
        self.grenade_generation_layout.addWidget(grenade_card_group, 0, 1, -1, 1)

        self.grenade_tab = QWidget()
        self.grenade_tab.setLayout(self.grenade_generation_layout)

    def get_tab(self):
        return self.grenade_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def generate_grenade(self):
        """ Handles performing the call to generate a grenade given the parameters and updating the Grenade Card image """
        # Load in properties that are currently set in the program
        grenade_name = self.grenade_line_edit.text()
        grenade_guild = self.guild_grenade_type_box.currentText()
        grenade_tier = self.tier_grenade_type_box.currentText()
        grenade_type = self.grenade_type_edit.text()
        grenade_damage = self.grenade_damage_edit.text()
        grenade_effect = self.grenade_effect_edit.text()
        grenade_form_check = self.form_fill_check.isChecked()
        grenade_art_path = self.art_filepath.text()

        # Generate a grenade
        grenade = Grenade(self.basedir, self.grenade_images,
                          name=grenade_name, guild=grenade_guild, grenade_type=grenade_type,
                          tier=grenade_tier, damage=grenade_damage, effect=grenade_effect, art_path=grenade_art_path)

        # Generate output name and check if it is already in use
        output_name = "{}_Tier{}_{}".format(grenade.guild, grenade.tier, grenade.name.replace(" ", "")) \
            if self.grenade_pdf_line_edit.text() == "" else self.grenade_pdf_line_edit.text()
        if output_name == self.current_grenade_pdf:
            self.output_grenade_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.grenade_pdf.generate_grenade_pdf(output_name, grenade, grenade_form_check)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_grenade(grenade, output_name)

        # Update the label and pdf name
        self.output_grenade_pdf_label.setText("Saved to output/grenades/{}.pdf!".format(output_name))
        self.current_grenade_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/grenades/{}.pdf".format(output_name))).as_uri()
        self.grenadeWebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_grenades(self):
        """ Handles generating and saving multiple grenade cards at once """
        # Error check for no number specified
        if self.numgrenade_line_edit.text() == "":
            self.grenade_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Load in properties that are currently set in the program
        grenade_guild = self.guild_grenade_type_box.currentText()
        grenade_tier = self.tier_grenade_type_box.currentText()
        grenade_type = self.grenade_type_edit.text()
        grenade_damage = self.grenade_damage_edit.text()
        grenade_effect = self.grenade_effect_edit.text()
        grenade_form_check = self.form_fill_check.isChecked()
        grenade_art_path = self.art_filepath.text()

        # Get a base output name to display and the number to generate
        output_name = self.current_grenade_pdf
        number_gen = int(self.numgrenade_line_edit.text())
        for _ in range(number_gen):
            # Generate a grenade
            grenade = Grenade(self.basedir, self.grenade_images,
                              guild=grenade_guild, grenade_type=grenade_type,
                              tier=grenade_tier, damage=grenade_damage, effect=grenade_effect,
                              art_path=grenade_art_path)

            # Generate output name and check if it is already in use
            output_name = "{}_Tier{}_{}".format(grenade.guild, grenade.tier, grenade.name.replace(" ", ""))
            if output_name == self.current_grenade_pdf:
                self.grenade_multi_output_label.setText("PDF Name already in use!".format(output_name))
                return

            # Generate the PDF
            self.grenade_pdf.generate_grenade_pdf(output_name, grenade, grenade_form_check)

            # FoundryVTT Check
            if self.foundry_export_check.isChecked() is True:
                self.foundry_translator.export_grenade(grenade, output_name)

        # Update the label and pdf name
        self.grenade_multi_output_label.setText("Saved {} potions to 'output/grenades/'!".format(number_gen))
        self.current_grenade_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/grenades/{}.pdf".format(output_name))).as_uri()
        self.grenadeWebBrowser.dynamicCall('Navigate(const QString&)', f)
