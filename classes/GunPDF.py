"""
@file GunPDF.py
@author Ryan Missel

Class to generate the PDF of the BnB Card Design for a given Gun.
"""
import os
import fitz
import pdfrw


class GunPDF:
    def __init__(self, base_dir):
        # Base executable directory
        self.base_dir = base_dir

        # KEY Names for PDF
        self.ANNOT_KEY = '/Annots'
        self.ANNOT_FIELD_KEY = '/T'
        self.ANNOT_VAL_KEY = '/V'
        self.ANNOT_RECT_KEY = '/Rect'
        self.SUBTYPE_KEY = '/Subtype'
        self.WIDGET_SUBTYPE_KEY = '/Widget'
        self.PARENT_KEY = '/Parent'

        # PDF Appearance for the Forms
        self.appearances = {
            "Damage": ('/Helvetica-BoldOblique 20.00 Tf 0 g', 1),
            "Name": ('/Helvetica-BoldOblique 0 Tf 0 g', 1),

            "Guild": ('/Helvetica-Bold 17.50 Tf 0 g', 1),
            "GunType": ('/Helvetica-Bold 17.50 Tf 0 g', 1),
            "Rarity": ('/Helvetica-Bold 0 Tf 0 g', 1),

            "ElementBonus": ('/Helvetica-Bold 13.00 Tf 0 g', 1),

            "Hit": ('/Helvetica-Bold 15.00 Tf 255 g', 0),
            "Crit": ('/Helvetica-Bold 15.00 Tf 255 g', 0),
            "Range": ('/Helvetica-Bold 25.00 Tf 0 g', 0),

            "RedText": ('/Helvetica-Bold 13.00 Tf 0 g', 0),
            "Prefix": ('/Helvetica-Bold 13.00 Tf 0 g', 0),
            "GuildMod": ('/Helvetica-Bold 13.00 Tf 0 g', 0),
        }

    def fill_pdf(self, input_pdf_path, output_pdf_path, data_dict):
        """
        Handles filling in the form fields of a given gun card PDF template with information
        from the generated gun
        :param input_pdf_path: path to the template PDF
        :param output_pdf_path: filename to save the PDF as
        :param data_dict: given dictionary mapping form field names to input
        """
        template_pdf = pdfrw.PdfReader(input_pdf_path)
        for page in template_pdf.pages:
            annotations = page[self.ANNOT_KEY]
            for annotation in annotations:
                if annotation[self.SUBTYPE_KEY] == self.WIDGET_SUBTYPE_KEY:
                    if annotation[self.PARENT_KEY][self.ANNOT_FIELD_KEY]:
                        key = annotation[self.PARENT_KEY][self.ANNOT_FIELD_KEY][1:-1]
                        if key in data_dict.keys():
                            if type(data_dict[key]) == bool:
                                if data_dict[key] is True:
                                    annotation.update(pdfrw.PdfDict(
                                        AS=pdfrw.PdfName('Yes')))
                            else:
                                # Get the appearance string
                                if 'Hit' in key or 'Crit' in key:
                                    display_string, q_value = self.appearances.get(key.split('_')[0])
                                else:
                                    display_string, q_value = self.appearances.get(key, ('/Helvetica-Bold 12.50 Tf 0 g', 0))

                                # Encode and update DisplayAppearance
                                PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode(display_string)
                                annotation[self.PARENT_KEY].update({'/DA': PDF_TEXT_APPEARANCE})

                                # Center text if given
                                if q_value == 1:
                                    annotation[self.PARENT_KEY].update(pdfrw.PdfDict(Q=q_value))

                                # Adding in the value given
                                annotation.update(
                                    pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                                )

                                # Change from fillable to static text
                                annotation[self.PARENT_KEY].update(pdfrw.PdfDict(Ff=1))
                                annotation.update(pdfrw.PdfDict(Ff=1))

                                # Update the AP of this annotation to nothing
                                annotation[self.PARENT_KEY].update(pdfrw.PdfDict(AP=''))

        # Force form appearance to show and output PDF
        template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))  # NEW
        pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

    def add_image_to_pdf(self, pdf_path, out_path, image, position):
        """
        Handles adding an image to a Pdf through the library PyMuPDF. Essentially layers two pages (page and image as a page)
        onto each other before compressing to one page
        :param pdf_path: filled out template
        :param out_path: output path for name
        :param image: image path to use
        :param position: where in the template to place the image
        """
        file_handle = fitz.open(pdf_path)

        page = file_handle[int(position['page']) - 1]
        page.insert_image(
            fitz.Rect(position['x0'], position['y0'],
            position['x1'], position['y1']),
            filename=image
        )
        file_handle.save(out_path)

    def generate_gun_pdf(self, output_name, gun, gun_images, rarity_border):
        """
        Handles generating a Gun Card PDF filled out with the information from the generated gun
        :param output_name: name of the output PDF to save
        """
        # Construct information string, including prefix info, redtext info, guild info
        # Essentially shifts up into higher boxes if the previous field is empty
        redtext_str = ''
        if gun.redtext_info is not None:
            redtext_str += "{:<12} {}: {}\n\n".format("(Red Text)", gun.redtext_name, gun.redtext_info)

        prefix_str = ''
        if gun.redtext_info is None and gun.prefix_info is not None:
            redtext_str += "{:<15} {}: {}\n\n".format("(Prefix)", gun.prefix_name, gun.prefix_info)
        elif gun.prefix_info is not None:
            prefix_str += "{:<15} {}: {}\n\n".format("(Prefix)", gun.prefix_name, gun.prefix_info)

        guild_str = ''
        if gun.redtext_info is None and gun.prefix_info is None and gun.guild_info is not None:
            redtext_str += "{:<15} {}: {}\n\n".format("(Guild)", gun.guild.title(), gun.guild_mod)
        elif gun.redtext_info is None and gun.prefix_info is not None and gun.guild_info is not None:
            prefix_str += "{:<15} {}: {}\n\n".format("(Guild)", gun.guild.title(), gun.guild_mod)
        elif gun.redtext_info is not None and gun.prefix_info is None and gun.guild_info is not None:
            prefix_str += "{:<15} {}: {}\n\n".format("(Guild)", gun.guild.title(), gun.guild_mod)
        elif gun.guild_info is not None:
            guild_str += "{:<15} {}: {}\n\n".format("(Guild)", gun.guild.title(), gun.guild_mod)

        # Construct element bonus string
        if type(gun.element) == str and len(gun.element.split(' ')) > 1:
            element_bonus_str = gun.element.split(' ')[-1]
        else:
            element_bonus_str = ""

        # Construct damage die string
        die_num, die_type = gun.damage.split('d')
        if int(die_num) > 1:
            die_string = "x{}".format(die_num)
        else:
            die_string = ""

        # Build up data dictionary to fill in PDF
        data_dict = {
            'Name': gun.name,
            "Guild": gun.guild.title(),
            "Rarity": gun.rarity.title(),

            "GunType": gun.rarity.title(),
            "DieNumber": die_string,

            'Range': str(gun.range),
            'Damage': str(gun.damage),

            "Hit_Low": '{}'.format(gun.accuracy['2-7']['hits']),
            "Hit_Medium": '{}'.format(gun.accuracy['8-15']['hits']),
            "Hit_High": '{}'.format(gun.accuracy['16+']['hits']),
            "Crit_Low": '{}'.format(gun.accuracy['2-7']['crits']),
            "Crit_Medium": '{}'.format(gun.accuracy['8-15']['crits']),
            "Crit_High": '{}'.format(gun.accuracy['16+']['crits']),

            "ElementBonus": element_bonus_str,

            "RedText": redtext_str,
            "Prefix": prefix_str,
            "GuildMod": guild_str,
            "ItemLevel": "Item Level: {}".format(gun.item_level)
        }

        # Fill the PDF with the given information
        self.fill_pdf(self.base_dir + 'resources/GunTemplate.pdf', self.base_dir + 'output/guns/' + output_name + '_temp.pdf', data_dict)

        # Get a gun sample and apply a colored border depending
        if rarity_border is True:
            gun_images.sample_gun_image(gun.type, gun.guild, rarity=gun.rarity)
        else:
            gun_images.sample_gun_image(gun.type, gun.guild, None)

        # Apply gun art to gun card
        position = {'page': 1, 'x0': 350, 'y0': 150, 'x1': 750, 'y1': 400}
        self.add_image_to_pdf(self.base_dir + 'output/guns/' + output_name + '_temp.pdf',
                         self.base_dir + 'output/guns/' + output_name + '_temp2.pdf',
                         self.base_dir + 'output/guns/temporary_gun_image.png',
                         position)

        # Apply gun icon to gun card
        gun_icon_paths = {
            "combat_rifle": "Combat rifle.png",
            "sniper_rifle": "Sniper rifle.png",
            "pistol": "Pistol.png",
            "shotgun": "Shotgun.png",
            "rocket_launcher": "Rocket launcher.png",
            "submachine_gun": "SMG.png"
        }

        position = {'page': 1, 'x0': 615, 'y0': 45, 'x1': 815, 'y1': 75}
        self.add_image_to_pdf(self.base_dir + 'output/guns/' + output_name + '_temp2.pdf',
                         self.base_dir + 'output/guns/' + output_name + '_temp3.pdf',
                         self.base_dir + 'resources/images/gun_icons/{}'.format(gun_icon_paths.get(gun.type)),
                         position)

        # Apply guild icon to gun card
        guild_icon_paths = {
            "alas!": "ALAS.png",
            "skuldugger": "SKULDUGGER.png",
            "dahlia": "DAHLIA.png",
            "blackpowder": "BLACKPOWDER.png",
            "malefactor": "MALEFACTOR.png",
            "hyperius": "HYPERIUS.png",
            "feriore": "FERIORE.png",
            "torgue": "TORGUE.png",
            "stoker": "STOKER.png",
        }

        position = {'page': 1, 'x0': 20, 'y0': 45, 'x1': 200, 'y1': 75}
        self.add_image_to_pdf(self.base_dir + 'output/guns/' + output_name + '_temp3.pdf',
                         self.base_dir + 'output/guns/' + output_name + '_temp4.pdf',
                         self.base_dir + 'resources/images/guild_icons/{}'.format(guild_icon_paths.get(gun.guild)),
                         position)

        # Apply damage die icon to gun card
        die_icon_paths = {
            "4": "1d4.png",
            "6": "1d6.png",
            "8": "1d8.png",
            "10": "1d10.png",
            "12": "1d12.png",
            "20": "1d20.png",
        }

        position = {'page': 1, 'x0': 75, 'y0': 280, 'x1': 115, 'y1': 330}
        self.add_image_to_pdf(self.base_dir + 'output/guns/' + output_name + '_temp4.pdf',
                         self.base_dir + 'output/guns/' + output_name + '_temp5.pdf',
                         self.base_dir + 'resources/images/die_icons/{}'.format(die_icon_paths.get(die_type)),
                         position)

        # Apply element icon to gun card
        element_icon_paths = {
            "cryo": "Cryo.png",
            "corrosive": "Corrosion.png",
            "corroshock": "CorroShock.png",
            "explosivcryo": "ExplosivCryo.png",
            "explosive": "Explosive.png",
            "incendiaradiation": "IncendiaRadiation.png",
            "incendiary": "Incendiary.png",
            "radiation": "Radiation.png",
            "shock": "Shock.png"
        }

        def convert_element(elements):
            """ Handles converting a given element of various types into the parseable element icon path """
            if elements is None:
                return None

            # If the element is a string, it is a single element. Check for added damage
            if type(elements) == str:
                return [elements.split(' ')[0]]

            # If input is a list, it has multiple elements. Check for combo elements.
            if type(elements) == list:
                returns = []

                if "corrosive" in elements and "shock" in elements:
                    returns.append("corroshock")
                elif "explosive" in elements and "cryo" in elements:
                    returns.append("explosivcryo")
                elif "incendiary" in elements and "radiation" in elements:
                    returns.append("incendiaradiation")

                # In the incredibly rare case there are 3 elements (high ele roll + prefix), add the third element
                if len(elements) > 2:
                    returns.append(elements[-1])

                return returns

        # Get the element converted to path
        element = convert_element(gun.element)

        # If there is no element, just rename the path
        if element is None:
            os.rename(self.base_dir + 'output/guns/' + output_name + '_temp5.pdf', self.base_dir + 'output/guns/' + output_name + '.pdf')

        # Otherwise add the element icon
        else:
            position = {'page': 1, 'x0': 60, 'y0': 440, 'x1': 110, 'y1': 470}
            self.add_image_to_pdf(self.base_dir + 'output/guns/' + output_name + '_temp5.pdf',
                             self.base_dir + 'output/guns/' + output_name + '_temp6.pdf',
                             self.base_dir + 'resources/images/element_icons/{}'.format(element_icon_paths.get(element[0])),
                             position)
            os.remove(self.base_dir + "output/guns/" + output_name + '_temp5.pdf')

            # In the event that there are 3 elements, add the third element as a separate icon below
            if len(element) == 2:
                position = {'page': 1, 'x0': 60, 'y0': 480, 'x1': 110, 'y1': 510}
                self.add_image_to_pdf(self.base_dir + 'output/guns/' + output_name + '_temp6.pdf',
                                 self.base_dir + 'output/guns/' + output_name + '.pdf',
                                 self.base_dir + 'resources/images/element_icons/{}'.format(element_icon_paths.get(element[1])),
                                 position)
                os.remove(self.base_dir + "output/guns/" + output_name + '_temp6.pdf')

            # Otherwise just rename to the final PDF
            else:
                os.rename(self.base_dir + 'output/guns/' + output_name + '_temp6.pdf', self.base_dir + 'output/guns/' + output_name + '.pdf')

        # Clean up temporary files
        os.remove(self.base_dir + "output/guns/" + output_name + '_temp.pdf')
        os.remove(self.base_dir + "output/guns/" + output_name + '_temp2.pdf')
        os.remove(self.base_dir + "output/guns/" + output_name + '_temp3.pdf')
        os.remove(self.base_dir + "output/guns/" + output_name + '_temp4.pdf')
        os.remove(self.base_dir + "output/guns/temporary_gun_image.png")