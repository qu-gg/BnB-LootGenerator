"""
@file RelicTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to relic generation
"""
import os
from pathlib import Path

from PyQt5.QtGui import QFont

from classes.Relic import Relic
from classes.RelicPDF import RelicPDF
from classes.RelicImage import RelicImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer, QtCore
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton, QCheckBox, QLineEdit,
                             QFileDialog)


class RelicTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(RelicTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.relic_images = RelicImage(self.basedir)
        self.relic_pdf = RelicPDF(self.basedir, self.statusbar, self.relic_images)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Relic Stats Grid    ###
        ###################################
        relic_stats_group = QGroupBox("Configuration")
        relic_stats_layout = QGridLayout()
        relic_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Relic Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Relic Name
        self.relic_line_edit = add_stat_to_layout(relic_stats_layout, "Relic Name:", idx, placeholder="Random")
        idx += 1

        # Relic % Selection
        relic_stats_layout.addWidget(QLabel("{:<15} ".format("Relic %:")), idx, 0)
        self.relic_id_box = QComboBox()
        self.relic_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/relics/relic.json").keys():
            self.relic_id_box.addItem(item)
        relic_stats_layout.addWidget(self.relic_id_box, idx, 1)
        idx += 1

        # Relic Type
        self.relic_type_edit = add_stat_to_layout(relic_stats_layout, "Relic Type:", idx)
        self.relic_type_edit.setToolTip("Either manually enter a relic type or let it be rolled.")
        idx += 1

        # Relic Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
        relic_stats_layout.addWidget(QLabel("Rarity: "), idx, 0)
        self.rarity_relic_type_box = QComboBox()
        for item in rarities:
            self.rarity_relic_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_relic_type_box, idx, 1)
        idx += 1

        # Relic Class
        rarities = ["Random", "Assassin", "Berserker", "Commando", "Gunzerker", "Hunter", "Mecromancer",
                    "Psycho", "Siren", "Soldier", "Any"]
        relic_stats_layout.addWidget(QLabel("Class: "), idx, 0)
        self.rarity_class_type_box = QComboBox()
        for item in rarities:
            self.rarity_class_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_class_type_box, idx, 1)
        idx += 1

        # Relic Effect
        self.relic_effect_edit = add_stat_to_layout(relic_stats_layout, "Effect:", idx)
        self.relic_effect_edit.setToolTip("Either manually enter a relic effect or let it be rolled.")
        idx += 1

        # Relic Class Effect
        self.relic_class_effect_edit = add_stat_to_layout(relic_stats_layout, "Class Effect:", idx)
        self.relic_class_effect_edit.setToolTip("Either manually enter a relic class effect or let it be rolled.")
        idx += 1

        # Add spacing between groups
        relic_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
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

        relic_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        relic_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        relic_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Rules/Misc Separator
        rules_separator = QLabel("Rules/Settings")
        rules_separator.setFont(font)
        rules_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(rules_separator, idx, 0, 1, -1)
        idx += 1

        # Whether to save the PDF as form-fillable still
        form_fill_label = QLabel("Keep PDF Form-Fillable:")
        form_fill_label.setStatusTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        relic_stats_layout.addWidget(form_fill_label, idx, 0)
        self.form_fill_check = QCheckBox()
        self.form_fill_check.setStatusTip("Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        relic_stats_layout.addWidget(self.form_fill_check, idx, 1)
        idx += 1

        # Add spacing between groups
        relic_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        relic_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        relic_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        relic_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        relic_stats_group.setLayout(relic_stats_layout)
        ###################################
        ###  END: Relic Stats Grid      ###
        ###################################

        ###################################
        ###  START: Relic Generation    ###
        ###################################
        relic_generation_group = QGroupBox("Single-Relic Generation")
        relic_generation_layout = QGridLayout()
        relic_generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.relic_pdf_line_edit = add_stat_to_layout(relic_generation_layout, "PDF Filename:", 0)
        self.relic_pdf_line_edit.setToolTip("Specify the filename that Generate Relic saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Relic")
        button.setToolTip("Handles generating the relic card and locally saving the PDF in \"outputs/relics/\".")
        button.clicked.connect(lambda: self.generate_relic())
        relic_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for save file output
        self.output_relic_pdf_label = QLabel()
        relic_generation_layout.addWidget(self.output_relic_pdf_label, 2, 0, 1, -1)

        # Grid layout
        relic_generation_group.setLayout(relic_generation_layout)
        ###################################
        ###  END: Relic Generation      ###
        ###################################

        ###################################
        ###  START: Multi Generation    ###
        ###################################
        relic_multi_group = QGroupBox("Multi-Relic Generation")
        relic_multi_layout = QGridLayout()
        relic_multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numrelic_line_edit = add_stat_to_layout(relic_multi_layout, "# Relics to Generate:", 0, force_int=True)
        self.numrelic_line_edit.setToolTip("Choose how many relics to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Relics")
        button.setToolTip("Handles generating the relics and locally saving their PDFs in \"outputs/relics/\".")
        button.clicked.connect(lambda: self.generate_multiple_relics())
        relic_multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.relic_multi_output_label = QLabel()
        relic_multi_layout.addWidget(self.relic_multi_output_label, 2, 0, 1, -1)

        # Grid layout
        relic_multi_group.setLayout(relic_multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Relic Display       ###
        ###################################
        relic_card_group = QGroupBox("Relic Card")
        relic_card_layout = QGridLayout()
        relic_card_layout.setAlignment(Qt.AlignVCenter)

        self.RelicWebBrowser = QAxContainer.QAxWidget(self)
        self.RelicWebBrowser.setFixedHeight(800)
        self.RelicWebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.RelicWebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                        "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        relic_card_layout.addWidget(self.RelicWebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_relic_pdf = "EXAMPLE_RELIC.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/examples/EXAMPLE_RELIC.pdf")).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        relic_card_group.setLayout(relic_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        relic_stats_group.setFixedWidth(300)
        relic_generation_group.setFixedWidth(300)
        relic_multi_group.setFixedWidth(300)
        relic_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        relic_stats_group.setFixedHeight(400)
        relic_generation_group.setFixedHeight(150)
        relic_multi_group.setFixedHeight(300)
        relic_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.relic_generation_layout = QGridLayout()
        self.relic_generation_layout.addWidget(relic_stats_group, 0, 0)
        self.relic_generation_layout.addWidget(relic_generation_group, 1, 0)
        self.relic_generation_layout.addWidget(relic_multi_group, 2, 0)
        self.relic_generation_layout.addWidget(relic_card_group, 0, 1, -1, 1)

        self.relic_tab = QWidget()
        self.relic_tab.setLayout(self.relic_generation_layout)

    def get_tab(self):
        return self.relic_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def generate_relic(self):
        """ Handles performing the call to generate a relic given the parameters and updating the Potion Card image """
        # Load in properties that are currently set in the program
        relic_id = self.relic_id_box.currentText()
        relic_name = self.relic_line_edit.text()
        relic_type = self.relic_type_edit.text()
        relic_rarity = self.rarity_relic_type_box.currentText()
        relic_effect = self.relic_effect_edit.text()
        relic_class_id = self.rarity_class_type_box.currentText()
        relic_class_effect = self.relic_class_effect_edit.text()
        relic_form_check = self.form_fill_check.isChecked()
        relic_art_path = self.art_filepath.text()

        # Generate a relic
        relic = Relic(self.basedir, self.relic_images,
                      relic_name, relic_id, relic_type, relic_rarity,
                      relic_effect, relic_class_id, relic_class_effect,
                      relic_art_path)

        # Generate output name and check if it is already in use
        output_name = f"{relic.class_id}_{relic.type}_{relic.name.replace(' ', '')}" \
            if self.relic_pdf_line_edit.text() == "" else self.relic_pdf_line_edit.text()
        if output_name == self.current_relic_pdf:
            self.output_relic_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.relic_pdf.generate_relic_pdf(output_name, relic, relic_form_check)

        # Update the label and pdf name
        self.output_relic_pdf_label.setText("Saved to output/relics/{}.pdf!".format(output_name))
        self.current_relic_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/relics/{}.pdf".format(output_name))).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_relic(relic, output_name)

    def generate_multiple_relics(self):
        """ Handles generating multiple relics and saving them to outputs/relics/ """
        # Error check for no number specified
        if self.numrelic_line_edit.text() == "":
            self.relic_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Load in properties that are currently set in the program
        relic_id = self.relic_id_box.currentText()
        relic_name = self.relic_line_edit.text()
        relic_type = self.relic_type_edit.text()
        relic_rarity = self.rarity_relic_type_box.currentText()
        relic_effect = self.relic_effect_edit.text()
        relic_class_id = self.rarity_class_type_box.currentText()
        relic_class_effect = self.relic_class_effect_edit.text()
        relic_form_check = self.form_fill_check.isChecked()
        relic_art_path = self.art_filepath.text()

        # Get a base output name to display and the number to generate
        output_name = self.current_relic_pdf
        number_gen = int(self.numrelic_line_edit.text())
        for _ in range(number_gen):
            # Generate a relic
            relic = Relic(self.basedir, self.relic_images,
                          relic_name, relic_id, relic_type, relic_rarity,
                          relic_effect, relic_class_id, relic_class_effect,
                          relic_art_path)

            # Generate output name and check if it is already in use
            output_name = f"{relic.class_id}_{relic.type}_{relic.name.replace(' ', '')}"
            if output_name == self.current_relic_pdf:
                self.relic_multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the PDF
            self.relic_pdf.generate_relic_pdf(output_name, relic, relic_form_check)

            # FoundryVTT Check
            if self.foundry_export_check.isChecked() is True:
                self.foundry_translator.export_relic(relic, output_name)

        # Update the label and pdf name
        self.relic_multi_output_label.setText("Saved {} potions to 'output/relics/'!".format(number_gen))
        self.current_relic_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/relics/{}.pdf".format(output_name))).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)
