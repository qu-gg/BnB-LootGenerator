"""
@file RelicTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to relic generation
"""
import os
from pathlib import Path

from classes.Relic import Relic
from classes.RelicPDF import RelicPDF
from classes.RelicImage import RelicImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton)


class RelicTab(QWidget):
    def __init__(self, basedir):
        super(RelicTab, self).__init__()

        # Load classes
        self.basedir = basedir

        # PDF and Image Classes
        self.relic_pdf = RelicPDF(self.basedir)
        self.relic_images = RelicImage(self.basedir)

        ###################################
        ###  BEGIN: Relic Stats Grid    ###
        ###################################
        relic_stats_group = QGroupBox("Configuration")
        relic_stats_layout = QGridLayout()
        relic_stats_layout.setAlignment(Qt.AlignTop)

        # Relic Name
        self.relic_line_edit = add_stat_to_layout(relic_stats_layout, "Relic Name:", 0, placeholder="Random")

        # Relic % Selection
        relic_stats_layout.addWidget(QLabel("{:<15} ".format("Relic %:")), 1, 0)
        self.relic_id_box = QComboBox()
        self.relic_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/relics/relic.json").keys():
            self.relic_id_box.addItem(item)
        relic_stats_layout.addWidget(self.relic_id_box, 1, 1)

        # Relic Type
        self.relic_type_edit = add_stat_to_layout(relic_stats_layout, "Relic Type:", 2, placeholder="Random")
        self.relic_type_edit.setToolTip("Either manually enter a relic type or let it be rolled.")

        # Relic Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
        relic_stats_layout.addWidget(QLabel("Rarity: "), 3, 0)
        self.rarity_relic_type_box = QComboBox()
        for item in rarities:
            self.rarity_relic_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_relic_type_box, 3, 1)

        # Relic Class
        rarities = ["Random", "Assassin", "Berserker", "Commando", "Gunzerker", "Hunter", "Mecromancer",
                    "Psycho", "Siren", "Soldier", "Any"]
        relic_stats_layout.addWidget(QLabel("Class: "), 4, 0)
        self.rarity_class_type_box = QComboBox()
        for item in rarities:
            self.rarity_class_type_box.addItem(item)
        relic_stats_layout.addWidget(self.rarity_class_type_box, 4, 1)

        # Relic Effect
        self.relic_effect_edit = add_stat_to_layout(relic_stats_layout, "Effect:", 5, placeholder="Random")
        self.relic_effect_edit.setToolTip("Either manually enter a relic effect or let it be rolled.")

        # Relic Class Effect
        self.relic_class_effect_edit = add_stat_to_layout(relic_stats_layout, "Class Effect:", 6, placeholder="Random")
        self.relic_class_effect_edit.setToolTip("Either manually enter a relic class effect or let it be rolled.")

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
        relic_stats_group.setFixedHeight(300)
        relic_generation_group.setFixedHeight(150)
        relic_multi_group.setFixedHeight(400)
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

        # Generate a relic
        relic = Relic(self.basedir, relic_name, relic_id, relic_type, relic_rarity,
                      relic_effect, relic_class_id, relic_class_effect)

        # Generate output name and check if it is already in use
        output_name = "{}_{}".format(relic.class_id, relic.name.replace(" ", "")) \
            if self.relic_pdf_line_edit.text() == "" else self.relic_pdf_line_edit.text()
        if output_name == self.current_relic_pdf:
            self.output_relic_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.relic_pdf.generate_relic_pdf(output_name, relic, self.relic_images)

        # Update the label and pdf name
        self.output_relic_pdf_label.setText("Saved to output/relics/{}.pdf!".format(output_name))
        self.current_relic_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/relics/{}.pdf".format(output_name))).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_relics(self):
        """ Handles generating multiple relics and saving them to outputs/relics/ """
        # Error check for no number specified
        if self.numrelic_line_edit.text() == "":
            self.relic_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Get a base output name to display and the number to generate
        output_name = self.current_relic_pdf
        number_gen = int(self.numrelic_line_edit.text())
        for _ in range(number_gen):
            # Generate a relic
            relic = Relic(self.basedir)

            # Generate output name and check if it is already in use
            output_name = "{}_{}".format(relic.class_id, relic.name.replace(" ", ""))
            if output_name == self.current_relic_pdf:
                self.relic_multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the PDF
            self.relic_pdf.generate_relic_pdf(output_name, relic, self.relic_images)

        # Update the label and pdf name
        self.relic_multi_output_label.setText("Saved {} potions to 'output/relics/'!".format(number_gen))
        self.current_relic_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/relics/{}.pdf".format(output_name))).as_uri()
        self.RelicWebBrowser.dynamicCall('Navigate(const QString&)', f)