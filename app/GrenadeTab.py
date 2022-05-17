"""
@file GrenadeTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to grenade generation
"""
import os
from pathlib import Path

from classes.Grenade import Grenade
from classes.GrenadePDF import GrenadePDF
from classes.GrenadeImage import GrenadeImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton)


class GrenadeTab(QWidget):
    def __init__(self, basedir):
        super(GrenadeTab, self).__init__()

        # Load classes
        self.basedir = basedir

        # PDF and Image Classes
        self.grenade_pdf = GrenadePDF(self.basedir)
        self.grenade_images = GrenadeImage(self.basedir)

        ###################################
        ###  BEGIN: Grenade Stats Grid    ###
        ###################################
        grenade_stats_group = QGroupBox("Configuration")
        grenade_stats_layout = QGridLayout()
        grenade_stats_layout.setAlignment(Qt.AlignTop)

        # grenade Name
        self.grenade_line_edit = add_stat_to_layout(grenade_stats_layout, "Grenade Name:", 0, placeholder="Random")

        # grenade Guild
        grenade_stats_layout.addWidget(QLabel("Guild: "), 1, 0)
        self.guild_grenade_type_box = QComboBox()
        self.guild_grenade_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/grenades/grenade.json").keys():
            self.guild_grenade_type_box.addItem(item)
        grenade_stats_layout.addWidget(self.guild_grenade_type_box, 1, 1)

        # grenade Tier
        grenade_stats_layout.addWidget(QLabel("Tier: "), 2, 0)
        self.tier_grenade_type_box = QComboBox()
        self.tier_grenade_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/grenades/grenade.json")["Ashen"].keys():
            self.tier_grenade_type_box.addItem(item)
        grenade_stats_layout.addWidget(self.tier_grenade_type_box, 2, 1)

        # Grenade Type
        self.grenade_type_edit = add_stat_to_layout(grenade_stats_layout, "Type:", 3, placeholder="Random")
        self.grenade_type_edit.setToolTip("Either manually enter a grenade type or let it be rolled.")

        # Grenade Damage
        self.grenade_damage_edit = add_stat_to_layout(grenade_stats_layout, "Damage:", 4, placeholder="NdX")
        self.grenade_damage_edit.setToolTip("Either manually enter a grenade damage stat or let it be rolled.")

        # Grenade Effect
        self.grenade_effect_edit = add_stat_to_layout(grenade_stats_layout, "Effect:", 5, placeholder="Random")
        self.grenade_effect_edit.setToolTip("Either manually enter a grenade effect or let it be rolled.")

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
        f = Path(os.path.abspath(self.basedir + "output/grenades/EXAMPLE_GRENADE.pdf")).as_uri()
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
        grenade_stats_group.setFixedHeight(300)
        grenade_generation_group.setFixedHeight(150)
        grenade_multi_group.setFixedHeight(350)
        grenade_card_group.setFixedHeight(800)

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

    def generate_grenade(self):
        """ Handles performing the call to generate a grenade given the parameters and updating the Grenade Card image """
        # Load in properties that are currently set in the program
        grenade_name = self.grenade_line_edit.text()
        grenade_guild = self.guild_grenade_type_box.currentText()
        grenade_tier = self.tier_grenade_type_box.currentText()
        grenade_type = self.grenade_type_edit.text()
        grenade_damage = self.grenade_damage_edit.text()
        grenade_effect = self.grenade_effect_edit.text()

        # Generate a grenade
        grenade = Grenade(self.basedir, name=grenade_name, guild=grenade_guild, grenade_type=grenade_type,
                          tier=grenade_tier, damage=grenade_damage, effect=grenade_effect)

        # Generate output name and check if it is already in use
        output_name = "{}_Tier{}_{}".format(grenade.guild, grenade.tier, grenade.name.replace(" ", "")) \
            if self.grenade_pdf_line_edit.text() == "" else self.grenade_pdf_line_edit.text()
        if output_name == self.current_grenade_pdf:
            self.output_grenade_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.grenade_pdf.generate_grenade_pdf(output_name, grenade, self.grenade_images)

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

        # Get a base output name to display and the number to generate
        output_name = self.current_grenade_pdf
        number_gen = int(self.numgrenade_line_edit.text())
        for _ in range(number_gen):
            # Generate a grenade
            grenade = Grenade(self.basedir, guild=grenade_guild, grenade_type=grenade_type,
                              tier=grenade_tier, damage=grenade_damage, effect=grenade_effect)

            # Generate output name and check if it is already in use
            output_name = "{}_Tier{}_{}".format(grenade.guild, grenade.tier, grenade.name.replace(" ", ""))
            if output_name == self.current_grenade_pdf:
                self.grenade_multi_output_label.setText("PDF Name already in use!".format(output_name))
                return

            # Generate the PDF
            self.grenade_pdf.generate_grenade_pdf(output_name, grenade, self.grenade_images)

        # Update the label and pdf name
        self.grenade_multi_output_label.setText("Saved {} potions to 'output/grenades/'!".format(number_gen))
        self.current_grenade_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/grenades/{}.pdf".format(output_name))).as_uri()
        self.grenadeWebBrowser.dynamicCall('Navigate(const QString&)', f)
