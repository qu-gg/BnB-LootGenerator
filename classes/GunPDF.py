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
            "NameFront": ('/Helvetica-BoldOblique 0 Tf 0 g', 1),

            "Rarity": ('/Helvetica-Bold 17 Tf 0 g', 1),
            "RarityFront": ('/Helvetica-Bold 17 Tf 0 g', 1),

            "Guild": ('/Helvetica-Bold 17.50 Tf 0 g', 1),
            "GunType": ('/Helvetica-Bold 17.50 Tf 0 g', 1),

            "ElementBonus": ('/Helvetica-Bold 13.00 Tf 0 g', 1),

            "Hit": ('/Helvetica-Bold 17.00 Tf 255 g', 1),
            "Crit": ('/Helvetica-Bold 17.00 Tf 255 g', 1),
            "Range": ('/Helvetica-Bold 25.00 Tf 0 g', 1),

            "RedText": ('/Helvetica-Bold 13.00 Tf 0 g', 1),
            "RedTextName": ('/Helvetica-Bold 13.00 Tf 0.80 0.27 0.29 rg', 1),

            "Prefix": ('/Helvetica-Bold 13.00 Tf 0 g', 1),
            "GuildMod": ('/Helvetica-Bold 13.00 Tf 0 g', 1),
            "GunMod": ('/Helvetica-Bold 13.00 Tf 0 g', 0),

            "EffectBox": ('/Helvetica-Bold 13.00 Tf 0 g', 1)
        }

        # File paths for the gun color backgrounds
        self.gun_colors_paths = {
            "legendary": "legendary_background.png",
            "epic": "epic_background.png",
            "rare": "rare_background.png",
            "uncommon": "uncommon_background.png",
            "common": "common_background.png"
        }

        # File paths for the gun icon images
        self.gun_icon_paths = {
            "combat_rifle": "Combat rifle.png",
            "sniper_rifle": "Sniper rifle.png",
            "pistol": "Pistol.png",
            "shotgun": "Shotgun.png",
            "rocket_launcher": "Rocket launcher.png",
            "submachine_gun": "SMG.png"
        }

        # File paths for the guild icon images
        self.guild_icon_paths = {
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

        # File paths for the die icon images
        self.die_icon_paths = {
            "4": "1d4.png",
            "6": "1d6.png",
            "8": "1d8.png",
            "10": "1d10.png",
            "12": "1d12.png",
            "20": "1d20.png",
        }

        # File paths for the element icon image
        self.element_icon_paths = {
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

    def convert_element(self, elements):
        """ Handles converting a given element of various types into the parseable element icon path """
        if elements is None:
            return None

        # If the element is a string, it is a single element. Check for added damage
        if type(elements) == str:
            return [elements.split(' ')[0]]

        # If input is a list, it has multiple elements. Check for combo elements.
        if type(elements) == list:
            returns = []

            # Combo element check
            if "corrosive" in elements and "shock" in elements:
                returns.append("corroshock")
            elif "explosive" in elements and "cryo" in elements:
                returns.append("explosivcryo")
            elif "incendiary" in elements and "radiation" in elements:
                returns.append("incendiaradiation")

            # Otherwise it is two separate, non-combined elements
            elif len(elements) == 2:
                returns = elements

            # In the incredibly rare case there are 3 elements (high ele roll + prefix), add the third element
            if len(elements) > 2:
                returns.append(elements[-1])

            return returns

    def fill_pdf(self, input_pdf_path, output_pdf_path, data_dict, form_check):
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
                                if form_check is False:
                                    annotation[self.PARENT_KEY].update(pdfrw.PdfDict(Ff=1))
                                    annotation.update(pdfrw.PdfDict(Ff=1))

                                # Update the AP of this annotation to nothing
                                annotation[self.PARENT_KEY].update(pdfrw.PdfDict(AP=''))

        # Force form appearance to show and output PDF
        template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))  # NEW
        pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

    def add_image_to_pdf(self, pdf_path, image, position):
        """
        Handles adding an image to a Pdf through the library PyMuPDF. Essentially layers two pages (page and image as a page)
        onto each other before compressing to one page
        :param pdf_path: filled out template
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

        temp_path = f'{self.base_dir}output/guns/temp.pdf'

        # Save output path as same name
        file_handle.save(temp_path)
        file_handle.close()

        # Clean up old pdf_path
        os.remove(pdf_path)
        os.rename(temp_path, pdf_path)

    def generate_gun_pdf(self, output_name, gun, gun_images, rarity_border, form_check, redtext_check):
        """
        Handles generating a Gun Card PDF filled out with the information from the generated gun
        :param output_name: name of the output PDF to save
        """
        # Output of the generated PDF
        output_path = f'{self.base_dir}output/guns/{output_name}.pdf'

        # Construct the effect box in the order of RedText, Prefix, Guild
        effect_str = ""
        if gun.redtext_info is not None and redtext_check is False:
            effect_str += f"[{gun.redtext_name}]\n"

            cur_chars = 0
            for idx, word in enumerate(gun.redtext_info.split(" ")):
                cur_chars += len(word)
                if cur_chars > 100:
                    effect_str += "\n"
                    cur_chars = 0

                effect_str += f" {word}"

            effect_str += "\n\n"

        if gun.prefix_info is not None:
            effect_str += f"[{gun.prefix_name}]\n"

            cur_chars = 0
            for idx, word in enumerate(gun.prefix_info.split(" ")):
                cur_chars += len(word)
                if cur_chars > 100:
                    effect_str += "\n"
                    cur_chars = 0

                effect_str += f" {word}"

            effect_str += "\n\n"

        if gun.guild_info is not None:
            effect_str += f"[{gun.guild.title()}]\n{gun.guild_mod}"

        # If the element list is a string, check all entries for a bonus die
        if type(gun.element) == list:
            element_bonus_str = ""
            for ele in gun.element:
                if '(' in ele or ')' in ele:
                    element_bonus_str = ele[ele.index('(') + 1:ele.index(')')]
                    gun.element[0] = ele.split(' ')[0]
        # If its just a string, its one element. Check it for bonus die
        elif type(gun.element) == str and len(gun.element.split(' ')) > 1:
            element_bonus_str = gun.element.split(' ')[-1]
        # Otherwise there is no element
        else:
            element_bonus_str = ""

        # Construct damage die string
        die_num, die_type = gun.damage.split('d')
        if int(die_num) > 1:
            die_string = "x{}".format(die_num)
        else:
            die_string = ""

        # Define if red text should be shown on front screen
        redtext_name_str = gun.redtext_name if gun.redtext_name is not None else ""

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

            "RedTextName": redtext_name_str,
            "ElementBonus": element_bonus_str,
            "EffectBox": effect_str
        }

        # Fill the PDF with the given information
        self.fill_pdf(self.base_dir + 'resources/GunTemplate.pdf', output_path, data_dict, form_check)

        # Get a gun sample
        gun_images.sample_gun_image(gun.type, gun.guild, None)

        # Add gun rarity color splash background
        if rarity_border:
            position = {'page': 1, 'x0': 350, 'y0': 140, 'x1': 750, 'y1': 390}
            self.add_image_to_pdf(output_path, f"{self.base_dir}resources/images/rarity_images/{self.gun_colors_paths.get(gun.rarity)}", position)

        # Apply gun art to gun card
        position = {'page': 1, 'x0': 350, 'y0': 140, 'x1': 750, 'y1': 390}
        self.add_image_to_pdf(output_path, self.base_dir + 'output/guns/temporary_gun_image.png', position)

        # Apply gun icon to gun card
        position = {'page': 1, 'x0': 615, 'y0': 45, 'x1': 815, 'y1': 75}
        self.add_image_to_pdf(output_path, f"{self.base_dir}resources/images/gun_icons/{self.gun_icon_paths.get(gun.type)}", position)

        # Apply guild icon to gun card
        position = {'page': 1, 'x0': 20, 'y0': 45, 'x1': 200, 'y1': 75}
        self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/guild_icons/{self.guild_icon_paths.get(gun.guild)}', position)

        # Apply damage die icon to gun card
        position = {'page': 1, 'x0': 75, 'y0': 280, 'x1': 115, 'y1': 330}
        self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/die_icons/{self.die_icon_paths.get(die_type)}', position)

        # Get the element converted to path
        element = self.convert_element(gun.element)

        # Apply element icon to gun card
        if element is not None:
            position = {'page': 1, 'x0': 60, 'y0': 440, 'x1': 110, 'y1': 470}
            self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/element_icons/{self.element_icon_paths.get(element[0])}', position)

            # In the event that there are 3 elements, add the third element as a separate icon below
            if len(element) == 2:
                position = {'page': 1, 'x0': 60, 'y0': 500, 'x1': 110, 'y1': 530}
                self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/element_icons/{self.element_icon_paths.get(element[1])}', position)

    def generate_split_gun_pdf(self, output_name, gun, gun_images, rarity_border, form_check, redtext_check):
        """
        Handles generating a Gun Card PDF that has two sides - one related to gun art only and the other related to gun
        information
        :param output_name: name of the output PDF to save
        """
        # Output of the generated PDF
        output_path = f'{self.base_dir}output/guns/{output_name}.pdf'

        # Construct the effect box in the order of RedText, Prefix, Guild
        effect_str = ""
        if gun.redtext_info is not None and redtext_check is False:
            effect_str += f"[{gun.redtext_name}]\n"

            cur_chars = 0
            for idx, word in enumerate(gun.redtext_info.split(" ")):
                cur_chars += len(word) + 1
                if cur_chars > 28:
                    effect_str += "\n"
                    cur_chars = 0

                effect_str += f" {word}"

            effect_str += "\n\n"

        if gun.prefix_info is not None:
            effect_str += f"[{gun.prefix_name}]\n"

            cur_chars = 0
            for idx, word in enumerate(gun.prefix_info.split(" ")):
                cur_chars += len(word) + 1
                if cur_chars > 28:
                    effect_str += "\n"
                    cur_chars = 0

                effect_str += f" {word}"

            effect_str += "\n\n"

        if gun.guild_info is not None:
            effect_str += f"[{gun.guild.title()}]\n{gun.guild_mod}"

        # Define if red text should be shown on front screen
        redtext_name_str = gun.redtext_name if gun.redtext_name is not None else ""

        # If the element list is a string, check all entries for a bonus die
        if type(gun.element) == list:
            element_bonus_str = ""
            for ele in gun.element:
                if '(' in ele or ')' in ele:
                    element_bonus_str = ele[ele.index('(') + 1:ele.index(')')]
                    gun.element[0] = ele.split(' ')[0]
        # If its just a string, its one element. Check it for bonus die
        elif type(gun.element) == str and len(gun.element.split(' ')) > 1:
            element_bonus_str = gun.element.split(' ')[-1]
        # Otherwise there is no element
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
            'NameFront': gun.name,

            "Rarity": f"{gun.rarity.title()} ({gun.item_level})",
            "RarityFront": f"{gun.rarity.title()} ({gun.item_level})",

            "DieNumber": die_string,
            'Range': str(gun.range),

            "Hit_Low": '{}'.format(gun.accuracy['2-7']['hits']),
            "Hit_Medium": '{}'.format(gun.accuracy['8-15']['hits']),
            "Hit_High": '{}'.format(gun.accuracy['16+']['hits']),
            "Crit_Low": '{}'.format(gun.accuracy['2-7']['crits']),
            "Crit_Medium": '{}'.format(gun.accuracy['8-15']['crits']),
            "Crit_High": '{}'.format(gun.accuracy['16+']['crits']),

            "ElementBonus": element_bonus_str,
            "RedTextName": redtext_name_str,
            "EffectBox": effect_str,
        }

        # Fill the PDF with the given information
        self.fill_pdf(self.base_dir + 'resources/GunTemplateSplitSmall.pdf', output_path, data_dict, form_check)

        # Get a gun sample
        gun_images.sample_gun_image(gun.type, gun.guild, None)

        # Add gun rarity color splash background
        if rarity_border:
            position = {'page': 2, 'x0': 100, 'y0': 125, 'x1': 500, 'y1': 375}
            self.add_image_to_pdf(output_path, f"{self.base_dir}resources/images/rarity_images/{self.gun_colors_paths.get(gun.rarity)}", position)

        # Apply gun art to gun card
        position = {'page': 2, 'x0': 100, 'y0': 125, 'x1': 500, 'y1': 375}
        self.add_image_to_pdf(output_path, self.base_dir + 'output/guns/temporary_gun_image.png', position)

        # Apply gun icon to gun card
        position = {'page': 1, 'x0': 480, 'y0': 25, 'x1': 580, 'y1': 55}
        self.add_image_to_pdf(output_path, f"{self.base_dir}resources/images/gun_icons/{self.gun_icon_paths.get(gun.type)}", position)

        position = {'page': 2, 'x0': 480, 'y0': 25, 'x1': 580, 'y1': 55}
        self.add_image_to_pdf(output_path, f"{self.base_dir}resources/images/gun_icons/{self.gun_icon_paths.get(gun.type)}", position)

        # Apply guild icon to gun card
        position = {'page': 1, 'x0': 25, 'y0': 25, 'x1': 125, 'y1': 55}
        self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/guild_icons/{self.guild_icon_paths.get(gun.guild)}', position)

        position = {'page': 2, 'x0': 25, 'y0': 25, 'x1': 125, 'y1': 55}
        self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/guild_icons/{self.guild_icon_paths.get(gun.guild)}', position)

        # Apply damage die icon to gun card
        position = {'page': 1, 'x0': 55, 'y0': 270, 'x1': 95, 'y1': 320}
        self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/die_icons/{self.die_icon_paths.get(die_type)}', position)

        # Get the element converted to path
        element = self.convert_element(gun.element)

        # Apply element icon to gun card
        if element is not None:
            position = {'page': 1, 'x0': 375, 'y0': 360, 'x1': 425, 'y1': 390}
            self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/element_icons/{self.element_icon_paths.get(element[0])}', position)

            # In the event that there are 3 elements, add the third element as a separate icon below
            if len(element) == 2:
                position = {'page': 1, 'x0': 410, 'y0': 360, 'x1': 460, 'y1': 390}
                self.add_image_to_pdf(output_path, f'{self.base_dir}resources/images/element_icons/{self.element_icon_paths.get(element[1])}', position)
