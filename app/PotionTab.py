"""
@file PotionTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to potion generation
"""
import os
from pathlib import Path

from classes.Potion import Potion
from classes.PotionPDF import PotionPDF
from classes.PotionImage import PotionImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton, QCheckBox)


class PotionTab(QWidget):
    def __init__(self, basedir):
        super(PotionTab, self).__init__()

        # Load classes
        self.basedir = basedir

        # PDF and Image Classes
        self.potion_pdf = PotionPDF(self.basedir)
        self.potion_images = PotionImage(self.basedir)

        ###################################
        ###  BEGIN: Potion Stats Grid   ###
        ###################################
        potion_stats_group = QGroupBox("Configuration")
        potion_stats_layout = QGridLayout()
        potion_stats_layout.setAlignment(Qt.AlignTop)

        # Potion ID Selection
        potion_stats_layout.addWidget(QLabel("Potion %: "), 0, 0)
        self.potion_id_box = QComboBox()
        self.potion_id_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/potions/potion.json").keys():
            self.potion_id_box.addItem(item)
        potion_stats_layout.addWidget(self.potion_id_box, 0, 1)

        # Whether to display the potion cost on the card or hide it
        potion_cost_text_label = QLabel("Display Potion Cost: ")
        potion_cost_text_label.setToolTip("Choose whether to put the potion cost on the gun card or not.")
        potion_stats_layout.addWidget(potion_cost_text_label, 1, 0)
        self.potion_cost = QCheckBox()
        self.potion_cost.setToolTip("Choose whether to put the potion cost on the gun card or not.")
        self.potion_cost.setChecked(True)
        potion_stats_layout.addWidget(self.potion_cost, 1, 1)

        # Whether to display the potion cost on the card or hide it
        potion_tina_text_label = QLabel("Display Tina Effect: ")
        potion_tina_text_label.setToolTip(
            "Choose whether to show the tina potion's effect for the player or have it read as 'SECRET EFFECT'")
        potion_stats_layout.addWidget(potion_tina_text_label, 2, 0)
        self.potion_tina_show = QCheckBox()
        self.potion_tina_show.setToolTip(
            "Choose whether to show the tina potion's effect for the player or have it read as 'SECRET EFFECT'")
        potion_stats_layout.addWidget(self.potion_tina_show, 2, 1)

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

    def generate_potion(self):
        """ Handles performing the call to generate a potion given the parameters and updating the Potion Card image """
        # Load in properties that are currently set in the program
        potion_id = self.potion_id_box.currentText()
        include_cost = self.potion_cost.isChecked()
        include_tina_effect = self.potion_tina_show.isChecked()

        # Generate a potion
        potion = Potion(self.basedir, potion_id)

        # Generate output name and check if it is already in use
        output_name = potion.name.replace(" ", "") if self.potion_pdf_line_edit.text() == "" else self.potion_pdf_line_edit.text()
        if output_name == self.current_potion_pdf:
            self.output_potion_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.potion_pdf.generate_potion_pdf(output_name, potion, self.potion_images, include_cost, include_tina_effect)

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

        # Get a base output name to display and the number to generate
        output_name = self.current_potion_pdf
        number_gen = int(self.numpotion_line_edit.text())
        for _ in range(number_gen):
            # Generate a potion
            potion = Potion(self.basedir, "Random")

            # Generate output name and check if it is already in use
            output_name = potion.name.replace(" ", "")
            if output_name == self.current_potion_pdf:
                self.potion_multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the PDF
            self.potion_pdf.generate_potion_pdf(output_name, potion, self.potion_images, include_cost, include_tina_effect)

        # Update the label and pdf name
        self.potion_multi_output_label.setText("Saved {} potions to 'output/potions/'!".format(number_gen))
        self.current_potion_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/potions/{}.pdf".format(output_name))).as_uri()
        self.PotionWebBrowser.dynamicCall('Navigate(const QString&)', f)