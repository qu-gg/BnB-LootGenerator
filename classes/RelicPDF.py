"""
@file RelicPDF.py
@author Ryan Missel

Class to generate the PDF of the BnB Card Design for a given relic.
"""
import os
import fitz
import pdfrw


class RelicPDF:
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

        # Rarity color mapping
        self.rarity_colors = {
            "common": "0 0 0",
            "uncommon": "0.24 0.82 0.04",
            "rare": "0.23 0.47 1.0",
            "epic": "0.57 0.25 0.78",
            "legendary": "1.0 0.71 0.0"
        }

        # PDF Appearance for the Forms
        self.appearances = {
            "Name": ('/Helvetica-BoldOblique 0 Tf 0 g', 0),
            "Rarity": ('/Helvetica-Bold 0 Tf 0 g', 1),
            "Effect": ('/Helvetica-Bold 16 Tf 0 g', 0),
            "ClassEffect": ('/Helvetica-Bold 16 Tf 0 g', 0),
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

    def generate_relic_pdf(self, output_name, relic, relic_images):
        """
        Handles generating a Gun Card PDF filled out with the information from the generated gun
        :param output_name: name of the output PDF to save
        """
        # Build up data dictionary to fill in PDF
        data_dict = {
            'Name': relic.name,
            "Rarity": relic.type,
            "Effect": "(Effect) {}".format(relic.effect),
            "ClassEffect": "({}) {}".format(relic.class_id, relic.class_effect),
            # "Type": relic.type
        }

        self.appearances["Rarity"] = ('/Helvetica-Bold 0 Tf 1 Tr {} rg'.format(self.rarity_colors[relic.rarity.lower()]), 1)

        # Fill the PDF with the given information
        self.fill_pdf(self.base_dir + 'resources/RelicTemplate.pdf',
                      self.base_dir + 'output/relics/' + output_name + '_temp.pdf', data_dict)

        # Get a relic image sample
        relic_images.sample_relic_image()

        # Apply gun art to gun card
        position = {'page': 1, 'x0': 90, 'y0': 150, 'x1': 346, 'y1': 406}
        self.add_image_to_pdf(
            self.base_dir + 'output/relics/' + output_name + '_temp.pdf',
            self.base_dir + 'output/relics/' + output_name + '.pdf',
            self.base_dir + 'output/relics/temporary_relic_image.png',
            position
        )

        # Remove old files
        os.remove(self.base_dir + "output/relics/" + output_name + '_temp.pdf')
        os.remove(self.base_dir + "output/relics/temporary_relic_image.png")
