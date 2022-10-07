"""
@file ShieldTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to shield generation
"""
import os
from pathlib import Path

from classes.Shield import Shield
from classes.ShieldPDF import ShieldPDF
from classes.ShieldImage import ShieldImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from PyQt5.QtCore import Qt
from PyQt5 import QAxContainer
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton)


class ShieldTab(QWidget):
    def __init__(self, basedir):
        super(ShieldTab, self).__init__()

        # Load classes
        self.basedir = basedir

        # PDF and Image Classes
        self.shield_pdf = ShieldPDF(self.basedir)
        self.shield_images = ShieldImage(self.basedir)

        ###################################
        ###  BEGIN: Shield Stats Grid    ###
        ###################################
        shield_stats_group = QGroupBox("Configuration")
        shield_stats_layout = QGridLayout()
        shield_stats_layout.setAlignment(Qt.AlignTop)

        # Shield Name
        self.shield_line_edit = add_stat_to_layout(shield_stats_layout, "Shield Name:", 0, placeholder="Random")

        # Shield Guild
        shield_stats_layout.addWidget(QLabel("Guild: "), 1, 0)
        self.guild_shield_type_box = QComboBox()
        self.guild_shield_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/shields/shield.json").keys():
            self.guild_shield_type_box.addItem(item)
        shield_stats_layout.addWidget(self.guild_shield_type_box, 1, 1)

        # Shield Tier
        shield_stats_layout.addWidget(QLabel("Tier: "), 2, 0)
        self.tier_shield_type_box = QComboBox()
        self.tier_shield_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/misc/shields/shield.json")["Ashen"].keys():
            self.tier_shield_type_box.addItem(item)
        shield_stats_layout.addWidget(self.tier_shield_type_box, 2, 1)

        # Shield Capacity
        self.shield_capacity_edit = add_stat_to_layout(shield_stats_layout, "Capacity:", 3, force_int=True)
        self.shield_capacity_edit.setToolTip("Either manually enter a shield capacity or let it be rolled.")

        # Shield Recharge
        self.shield_recharge_edit = add_stat_to_layout(shield_stats_layout, "Recharge Rate:", 4, force_int=True)
        self.shield_recharge_edit.setToolTip("Either manually enter a shield recharge rate or let it be rolled.")

        # Shield Effect
        self.shield_effect_edit = add_stat_to_layout(shield_stats_layout, "Effect:", 5, placeholder="Random")
        self.shield_effect_edit.setToolTip("Either manually enter a shield effect or let it be rolled.")

        # Grid layout
        shield_stats_group.setLayout(shield_stats_layout)
        ###################################
        ###  END: shield Stats Grid      ###
        ###################################

        ###################################
        ###  START: shield Generation    ###
        ###################################
        shield_generation_group = QGroupBox("Single-Shield Generation")
        shield_generation_layout = QGridLayout()
        shield_generation_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.shield_pdf_line_edit = add_stat_to_layout(shield_generation_layout, "PDF Filename:", 0)
        self.shield_pdf_line_edit.setToolTip("Specify the filename that Generate shield saves the next gun under.")

        # Generate button
        button = QPushButton("Generate Shield")
        button.setToolTip("Handles generating the shield card and locally saving the PDF in \"outputs/shields/\".")
        button.clicked.connect(lambda: self.generate_shield())
        shield_generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for save file output
        self.output_shield_pdf_label = QLabel()
        shield_generation_layout.addWidget(self.output_shield_pdf_label, 2, 0, 1, -1)

        # Grid layout
        shield_generation_group.setLayout(shield_generation_layout)
        ###################################
        ###  END: shield Generation      ###
        ###################################

        ###################################
        ###  START: Multi Generation    ###
        ###################################
        shield_multi_group = QGroupBox("Multi-Shield Generation")
        shield_multi_layout = QGridLayout()
        shield_multi_layout.setAlignment(Qt.AlignTop)

        # PDF Output Name
        self.numshield_line_edit = add_stat_to_layout(shield_multi_layout, "# Shields to Generate:", 0, force_int=True)
        self.numshield_line_edit.setToolTip("Choose how many shields to automatically generate and save.")

        # Generate button
        button = QPushButton("Generate Multiple Shields")
        button.setToolTip("Handles generating the shields and locally saving their PDFs in \"outputs/shields/\".")
        button.clicked.connect(lambda: self.generate_multiple_shields())
        shield_multi_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.shield_multi_output_label = QLabel()
        shield_multi_layout.addWidget(self.shield_multi_output_label, 2, 0, 1, -1)

        # Grid layout
        shield_multi_group.setLayout(shield_multi_layout)
        ###################################
        ###  END: Multi Generation      ###
        ###################################

        ###################################
        ###  START: Shield Display       ###
        ###################################
        shield_card_group = QGroupBox("Shield Card")
        shield_card_layout = QGridLayout()
        shield_card_layout.setAlignment(Qt.AlignVCenter)

        self.shieldWebBrowser = QAxContainer.QAxWidget(self)
        self.shieldWebBrowser.setFixedHeight(800)
        self.shieldWebBrowser.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.shieldWebBrowser.setToolTip("If nothing is displaying or the text is not displaying, then either "
                                        "1.) you do not have a local PDF Viewer or 2.) the OS you are on doesn't support annotation rendering.")
        shield_card_layout.addWidget(self.shieldWebBrowser, 0, 1, -1, 1)

        # Need to check if attempting to re-save when the PDF name is already taken
        self.current_shield_pdf = "EXAMPLE_SHIELD.pdf"

        # Load in Gun Card Template
        f = Path(os.path.abspath(self.basedir + "output/shields/EXAMPLE_SHIELD.pdf")).as_uri()
        self.shieldWebBrowser.dynamicCall('Navigate(const QString&)', f)

        # Grid layout
        shield_card_group.setLayout(shield_card_layout)
        ###################################
        ###  END: Potion Display        ###
        ###################################

        # Setting appropriate column widths
        shield_stats_group.setFixedWidth(300)
        shield_generation_group.setFixedWidth(300)
        shield_multi_group.setFixedWidth(300)
        shield_card_group.setFixedWidth(1000)

        # Setting appropriate layout heights
        shield_stats_group.setFixedHeight(300)
        shield_generation_group.setFixedHeight(150)
        shield_multi_group.setFixedHeight(400)
        shield_card_group.setFixedHeight(850)

        # Potion Generation Layout
        self.shield_generation_layout = QGridLayout()
        self.shield_generation_layout.addWidget(shield_stats_group, 0, 0)
        self.shield_generation_layout.addWidget(shield_generation_group, 1, 0)
        self.shield_generation_layout.addWidget(shield_multi_group, 2, 0)
        self.shield_generation_layout.addWidget(shield_card_group, 0, 1, -1, 1)

        self.shield_tab = QWidget()
        self.shield_tab.setLayout(self.shield_generation_layout)

    def get_tab(self):
        return self.shield_tab

    def generate_shield(self):
        """ Handles performing the call to generate a shield given the parameters and updating the Shield Card image """
        # Load in properties that are currently set in the program
        shield_name = self.shield_line_edit.text()
        shield_guild = self.guild_shield_type_box.currentText()
        shield_tier = self.tier_shield_type_box.currentText()
        shield_capacity = str(self.shield_capacity_edit.text())
        shield_recharge = str(self.shield_recharge_edit.text())
        shield_effect = self.shield_effect_edit.text()

        # Generate a shield
        shield = Shield(self.basedir, name=shield_name, guild=shield_guild, tier=shield_tier,
                        capacity=shield_capacity, recharge=shield_recharge, effect=shield_effect)

        # Generate output name and check if it is already in use
        output_name = "{}_Tier{}_{}".format(shield.guild, shield.tier, shield.name.replace(" ", "")) \
            if self.shield_pdf_line_edit.text() == "" else self.shield_pdf_line_edit.text()
        if output_name == self.current_shield_pdf:
            self.output_shield_pdf_label.setText("PDF Name already in use!".format(output_name))
            return

        # Generate the PDF
        self.shield_pdf.generate_shield_pdf(output_name, shield, self.shield_images)

        # Update the label and pdf name
        self.output_shield_pdf_label.setText("Saved to output/shields/{}.pdf!".format(output_name))
        self.current_shield_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/shields/{}.pdf".format(output_name))).as_uri()
        self.shieldWebBrowser.dynamicCall('Navigate(const QString&)', f)

    def generate_multiple_shields(self):
        """ Handles generating and saving multiple shield cards at once """
        # Error check for no number specified
        if self.numshield_line_edit.text() == "":
            self.shield_multi_output_label.setText("No number set! Enter a number and resubmit!")
            return

        # Load in properties that are currently set in the program
        shield_guild = self.guild_shield_type_box.currentText()
        shield_tier = self.tier_shield_type_box.currentText()
        shield_capacity = str(self.shield_capacity_edit.text())
        shield_recharge = str(self.shield_recharge_edit.text())
        shield_effect = self.shield_effect_edit.text()

        # Get a base output name to display and the number to generate
        output_name = self.current_shield_pdf
        number_gen = int(self.numshield_line_edit.text())
        for _ in range(number_gen):
            # Generate a shield
            shield = Shield(self.basedir, guild=shield_guild, tier=shield_tier, capacity=shield_capacity,
                            recharge=shield_recharge, effect=shield_effect)

            # Generate output name and check if it is already in use
            output_name = "{}_Tier{}_{}".format(shield.guild, shield.tier, shield.name.replace(" ", ""))
            if output_name == self.current_shield_pdf:
                self.shield_multi_output_label.setText("PDF Name already in use!".format(output_name))
                continue

            # Generate the PDF
            self.shield_pdf.generate_shield_pdf(output_name, shield, self.shield_images)

        # Update the label and pdf name
        self.shield_multi_output_label.setText("Saved {} potions to 'output/shields/'!".format(number_gen))
        self.current_shield_pdf = output_name

        # Load in gun card PDF
        f = Path(os.path.abspath("output/shields/{}.pdf".format(output_name))).as_uri()
        self.shieldWebBrowser.dynamicCall('Navigate(const QString&)', f)
