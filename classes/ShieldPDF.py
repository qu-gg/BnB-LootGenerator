"""
@file ShieldPDF.py
@author Ryan Missel

Class to generate the PDF of the BnB Card Design for a given Shield.
"""
import os
import fitz
import pdfrw


class ShieldPDF:
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
            "Name": ('/Helvetica-BoldOblique 0 Tf 0 g', 0),
            "Tier": ('/Helvetica-Bold 0 Tf 0 g', 0),
            "Capacity": ('/Helvetica-Bold 0 Tf 0 g', 1),
            "Recharge": ('/Helvetica-Bold 0 Tf 0 g', 1),
            "Effect": ('/Helvetica-Bold 0 Tf 0 g', 1),
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

    def generate_shield_pdf(self, output_name, shield, shield_images):
        """
        Handles generating a Gun Card PDF filled out with the information from the generated gun
        :param output_name: name of the output PDF to save
        """
        # Build up the effect string
        effect_str = ""
        for idx, word in enumerate(shield.effect.split(" ")):
            if idx % 10 == 0 and idx != 0:
                effect_str += '\n'

            effect_str += word + " "

        # Build up data dictionary to fill in PDF
        data_dict = {
            'Name': shield.name,
            "Tier": shield.tier,
            "Capacity": shield.capacity,
            "Recharge": shield.recharge,
            "Effect": effect_str,
        }

        # Fill the PDF with the given information
        self.fill_pdf(self.base_dir + 'resources/ShieldTemplate.pdf',
                      self.base_dir + 'output/shields/' + output_name + '_temp.pdf', data_dict)

        # Get a shield image sample
        shield_images.sample_shield_image()

        # Apply shield art to shield card
        position = {'page': 1, 'x0': 140, 'y0': 150, 'x1': 376, 'y1': 406}
        self.add_image_to_pdf(
            self.base_dir + 'output/shields/' + output_name + '_temp.pdf',
            self.base_dir + 'output/shields/' + output_name + '_temp2.pdf',
            self.base_dir + 'output/shields/temporary_shield_image.png',
            position
        )

        # Apply guild icon to gun card
        guild_icon_paths = {
            "Ashen": "ASHEN.png",
            "Alas!": "ALAS.png",
            "Dahlia": "DAHLIA.png",
            "Feriore": "FERIORE.png",
            "Malefactor": "MALEFACTOR.png",
            "Pangoblin": "PANGOBLIN.png",
            "Stoker": "STOKER.png",
            "Torgue": "TORGUE.png"
        }

        position = {'page': 1, 'x0': 300, 'y0': 45, 'x1': 425, 'y1': 75}
        self.add_image_to_pdf(
            self.base_dir + 'output/shields/' + output_name + '_temp2.pdf',
            self.base_dir + 'output/shields/' + output_name + '.pdf',
            self.base_dir + 'resources/images/guild_icons/{}'.format(guild_icon_paths.get(shield.guild)),
            position
        )

        # Remove old files
        os.remove(self.base_dir + "output/shields/" + output_name + '_temp.pdf')
        os.remove(self.base_dir + "output/shields/" + output_name + '_temp2.pdf')