"""
@file GrenadePDF.py
@author Ryan Missel

Class to generate the PDF of the BnB Card Design for a given Grenade.
"""
import os
import fitz
import pdfrw
import requests
from PIL import Image


class GrenadePDF:
    def __init__(self, base_dir, statusbar, grenade_images):
        # Base executable directory
        self.base_dir = base_dir
        self.statusbar = statusbar

        # Image class
        self.grenade_images = grenade_images

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
            "Name": ('/Helvetica-BoldOblique 0 Tf 0 g', 0),
            "Tier": ('/Helvetica-Bold 0 Tf 0 g', 0),
            "Damage": ('/Helvetica-Bold 0 Tf 0 g', 1),
            "Effect": ('/Helvetica-Bold 0 Tf 0 g', 1),
        }

        # Guild icon image paths
        self.guild_icon_paths = {
            "Ashen": "ASHEN.png",
            "Dahlia": "DAHLIA.png",
            "Feriore": "FERIORE.png",
            "Hyperius": "HYPERIUS.png",
            "Malefactor": "MALEFACTOR.png",
            "Pangoblin": "PANGOBLIN.png",
            "Stoker": "STOKER.png",
            "Torgue": "TORGUE.png"
        }

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

        temp_path = f'{self.base_dir}output/guns/temp.pdf'

        # Save output path as same name
        file_handle.save(temp_path)
        file_handle.close()

        # Clean up old pdf_path
        os.remove(pdf_path)
        os.rename(temp_path, pdf_path)

    def generate_grenade_pdf(self, output_name, grenade, form_check):
        """
        Handles generating a Gun Card PDF filled out with the information from the generated gun
        :param output_name: name of the output PDF to save
        """
        # Output of the generated PDF
        output_path = f'{self.base_dir}output/grenades/{output_name}.pdf'

        # Build up the effect string
        effect_str = "({})\n".format(grenade.type)
        for idx, word in enumerate(grenade.effect.split(" ")):
            if idx % 10 == 0 and idx != 0:
                effect_str += '\n'

            effect_str += word + " "

        # Build up data dictionary to fill in PDF
        data_dict = {
            'Name': grenade.name,
            "Tier": grenade.tier,
            "Damage": grenade.damage,
            "Effect": effect_str,
        }

        # Fill the PDF with the given information
        self.fill_pdf(self.base_dir + 'resources/GrenadeTemplate.pdf', output_path, data_dict, form_check)

        # Apply grenade art to grenade card
        position = {'page': 1, 'x0': 140, 'y0': 150, 'x1': 376, 'y1': 406}
        art_success = True

        # Try local path first
        try:
            self.add_image_to_pdf(output_path, grenade.art_path, position)
        except:
            art_success = False

        # Then try URL on failure
        if art_success is False:
            try:
                # Get image and then save locally temporarily
                response = requests.get(grenade.art_path, stream=True)
                img = Image.open(response.raw)
                img.save(self.base_dir + 'output/grenades/temporary_grenade_image.png')
                self.add_image_to_pdf(output_path, self.base_dir + 'output/grenades/temporary_grenade_image.png', position)
                art_success = True
            except:
                self.statusbar.clearMessage()
                self.statusbar.showMessage("Invalid URL or filepath when trying to open, defaulting to normal image!", 5000)
                art_success = False

        # If no URL/File given or invalid paths, then sample a grenade
        if art_success is False:
            self.grenade_images.sample_grenade_image()
            self.add_image_to_pdf(output_path, self.base_dir + 'output/grenades/temporary_grenade_image.png', position)

        # Apply guild icon to grenade card
        position = {'page': 1, 'x0': 300, 'y0': 45, 'x1': 425, 'y1': 75}
        self.add_image_to_pdf(output_path, f"{self.base_dir}resources/images/guild_icons/{self.guild_icon_paths.get(grenade.guild)}", position)
