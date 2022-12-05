"""
@file PotionTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to potion generation
"""
import os
from pathlib import Path

from PyQt5.QtGui import QFont

from classes.Potion import Potion
from classes.PotionPDF import PotionPDF
from classes.PotionImage import PotionImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer, QtCore
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton, QCheckBox, QLineEdit,
                             QFileDialog)


class PotionTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(PotionTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        self.potion_images = PotionImage(self.basedir)
        self.potion_pdf = PotionPDF(self.basedir, self.statusbar, self.potion_images)

        # API Classes
        self.foundry_translator = foundry_translator

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ###################################
        ###  BEGIN: Potion Stats Grid   ###
        ###################################
        potion_stats_group = QGroupBox("Configuration")
        potion_stats_layout = QGridLayout()
        potion_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        ##### Information Separator
        information_separator = QLabel("Potion Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Potion ID Selection
        potion_stats_layout.addWidget(QLabel("Potion %: "), idx, 0)
        self.potion_id_box = QComboBox()
        self.potion_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/potions/potion.json").keys():
            self.potion_id_box.addItem(item)
        potion_stats_layout.addWidget(self.potion_id_box, idx, 1)
        idx += 1

        # Whether to display the potion cost on the card or hide it
        potion_cost_text_label = QLabel("Display Potion Cost: ")
        potion_cost_text_label.setToolTip("Choose whether to put the potion cost on the gun card or not.")
        potion_stats_layout.addWidget(potion_cost_text_label, idx, 0)
        self.potion_cost = QCheckBox()
        self.potion_cost.setToolTip("Choose whether to put the potion cost on the gun card or not.")
        self.potion_cost.setChecked(True)
        potion_stats_layout.addWidget(self.potion_cost, idx, 1)
        idx += 1

        # Whether to display the potion cost on the card or hide it
        potion_tina_text_label = QLabel("Display Tina Effect: ")
        potion_tina_text_label.setToolTip(
            "Choose whether to show the tina potion's effect for the player or have it read as 'SECRET EFFECT'")
        potion_stats_layout.addWidget(potion_tina_text_label, idx, 0)
        self.potion_tina_show = QCheckBox()
        self.potion_tina_show.setToolTip(
            "Choose whether to show the tina potion's effect for the player or have it read as 'SECRET EFFECT'")
        potion_stats_layout.addWidget(self.potion_tina_show, idx, 1)
        idx += 1

        # Add spacing between groups
        potion_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
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

        potion_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        potion_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Add spacing between groups
        potion_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Rules/Misc Separator
        rules_separator = QLabel("Rules/Settings")
        rules_separator.setFont(font)
        rules_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(rules_separator, idx, 0, 1, -1)
        idx += 1

        # Whether to save the PDF as form-fillable still
        form_fill_label = QLabel("Keep PDF Form-Fillable:")
        form_fill_label.setStatusTip(
            "Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        potion_stats_layout.addWidget(form_fill_label, idx, 0)
        self.form_fill_check = QCheckBox()
        self.form_fill_check.setStatusTip(
            "Choose whether to keep the PDF unflattened so filled forms can be modified in a PDF editor.")
        potion_stats_layout.addWidget(self.form_fill_check, idx, 1)
        idx += 1

        # Add spacing between groups
        potion_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### External Tools Separator
        api_separator = QLabel("External Tools")
        api_separator.setFont(font)
        api_separator.setAlignment(QtCore.Qt.AlignCenter)
        potion_stats_layout.addWidget(api_separator, idx, 0, 1, -1)
        idx += 1

        # FoundryVTT JSON flag
        foundry_export_label = QLabel("FoundryVTT JSON Export: ")
        foundry_export_label.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        potion_stats_layout.addWidget(foundry_export_label, idx, 0)
        self.foundry_export_check = QCheckBox()
        self.foundry_export_check.setStatusTip(
            "Choose whether to output a JSON file that can be imported by the B&B FoundryVTT System.")
        self.foundry_export_check.setChecked(False)
        potion_stats_layout.addWidget(self.foundry_export_check, idx, 1)
        idx += 1

        # Grid layout
        potion_stats_group.setLayout(potion_stats_layout)
        ###################################
        ###  END: Potion Stats Grid     ###
        ###################################

        ###################################
        ###  START: Potion Generation   ###
        ###################################
        potion_generation_group = QGroupBox("Single-Potion Generation")
        potion_generation_layout = QGridLayout()
        potion_generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.potion_pdf_line_edit = add_stat_to_layout(potion_generation_layout, "PDF Filename:", 0)
        self.potion_pdf_line_edit.setToolTip("Specify the filename that Generate Gun saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Potion")
        button.setToolTip("Handles generating the potion card and locally saving the PDF in \"outputs/\".")
        button.clicked.connect(lambda: self.generate_potion())
        potion_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.output_potion_pdf_label = QLabel()
        potion_generation_layout.addWidget(self.output_potion_pdf_label, 2, 0, 1, -1)

        # Grid layout
        potion_generation_group.setLayout(potion_generation_layout)
        ###################################
        ###  END: Potion Generation     ###
        ###################################

        ###################################
        ###  START: Multi Generation    ###
        ###################################
        potion_multi_group = QGroupBox("Multi-Potion Generation")
        potion_multi_layout = QGridLayout()
        potion_multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numpotion_line_edit = add_stat_to_layout(potion_multi_layout, "# Potions to Generate:", 0, force_int=True)
        self.numpotion_line_edit.setToolTip("Choose how many potions to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Potions")
        button.setToolTip("Handles generating the potions and locally saving their PDFs in \"outputs/potions/\".")
        button.clicked.connect(lambda: self.generate_multiple_potions())
        potion_multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.potion_multi_output_label = QLabel()
        potion_multi_layout.addWidget(self.potion_multi_output_label, 2, 0, 1, -1)

        # Grid layout
        potion_multi_group.setLayout(potion_multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Potion Display      ###
        ###################################
        potion_card_group = QGroupBox("Potion Card")
        potion_card_layout = QGridLayout()
        potion_card_layout.setAlignment(Qt.AlignVCenter)

        self.PotionWebBrowser = QAxContainer.QAxWidget(self)
        self.PotionWebBrowser.setFixedHeight(800)
        self.PotionWebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.PotionWebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                         "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        potion_card_layout.addWidget(self.PotionWebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_potion_pdf = "EXAMPLE_POTION.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/examples/EXAMPLE_POTION.pdf")).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        potion_card_group.setLayout(potion_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        potion_stats_group.setFixedWidth(300)
        potion_generation_group.setFixedWidth(300)
        potion_multi_group.setFixedWidth(300)
        potion_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        potion_stats_group.setFixedHeight(300)
        potion_generation_group.setFixedHeight(150)
        potion_multi_group.setFixedHeight(400)
        potion_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.potion_generation_layout = QGridLayout()
        self.potion_generation_layout.addWidget(potion_stats_group, 0, 0)
        self.potion_generation_layout.addWidget(potion_generation_group, 1, 0)
        self.potion_generation_layout.addWidget(potion_multi_group, 2, 0)
        self.potion_generation_layout.addWidget(potion_card_group, 0, 1, -1, 1)

        self.potion_tab = QWidget()
        self.potion_tab.setLayout(self.potion_generation_layout)

    def get_tab(self):
        return self.potion_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def generate_potion(self):
        """ Handles performing the call to generate a potion given the parameters and updating the Potion Card image """
        # Load in properties that are currently set in the program
        potion_id = self.potion_id_box.currentText()
        include_cost = self.potion_cost.isChecked()
        include_tina_effect = self.potion_tina_show.isChecked()
        potion_form_check = self.form_fill_check.isChecked()
        potion_art_path = self.art_filepath.text()

        # Generate a potion
        potion = Potion(self.basedir, self.potion_images, potion_id, potion_art_path)

        # Generate output name and check if it is already in use
        output_name = potion.name.replace(" ", "") if self.potion_pdf_line_edit.text() == "" else self.potion_pdf_line_edit.text()
        if output_name == self.current_potion_pdf:
            self.output_potion_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.potion_pdf.generate_potion_pdf(output_name, potion, self.potion_images,
                                            include_cost, include_tina_effect, potion_form_check)

        # FoundryVTT Check
        if self.foundry_export_check.isChecked() is True:
            self.foundry_translator.export_potion(potion, output_name)

        # Update the label and pdf name
        self.output_potion_pdf_label.setText("Saved to output/potions/{}.pdf!".format(output_name))
        self.current_potion_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/potions/{}.pdf".format(output_name))).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_potions(self):
        """ Handles generating multiple potions at once and saving them to outputs/potions/ """
        # Error check for no number specified
        if self.numpotion_line_edit.text() == "":
            self.potion_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Load in properties that are currently set in the program
        include_cost = self.potion_cost.isChecked()
        include_tina_effect = self.potion_tina_show.isChecked()
        potion_form_check = self.form_fill_check.isChecked()
        potion_art_path = self.art_filepath.text()

        # Get a base output name to display and the number to generate
        output_name = self.current_potion_pdf
        number_gen = int(self.numpotion_line_edit.text())
        for _ in range(number_gen):
            # Generate a potion
            potion = Potion(self.basedir, self.potion_images, "Random", potion_art_path)

            # Generate output name and check if it is already in use
            output_name = potion.name.replace(" ", "")
            if output_name == self.current_potion_pdf:
                self.potion_multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the PDF
            self.potion_pdf.generate_potion_pdf(output_name, potion, self.potion_images,
                                                include_cost, include_tina_effect, potion_form_check)

            # FoundryVTT Check
            if self.foundry_export_check.isChecked() is True:
                self.foundry_translator.export_potion(potion, output_name)

        # Update the label and pdf name
        self.potion_multi_output_label.setText("Saved {} potions to 'output/potions/'!".format(number_gen))
        self.current_potion_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/potions/{}.pdf".format(output_name))).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)