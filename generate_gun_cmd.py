"""
@file generate_gun_cmd.py
@author Ryan Missel

Command line based script for users to generate guns and get a PDF of the BnB Card Design
filled out by the gun attributes that are generated.

Takes in user-input on specific gun features to choose
"""
import os
import fitz
import pdfrw
import argparse

from classes.Gun import Gun
from classes.GunImage import GunImage

# KEY Names for PDF
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'
PARENT_KEY = '/Parent'


def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    """
    Handles filling in the form fields of a given gun card PDF template with information
    from the generated gun
    :param input_pdf_path: path to the template PDF
    :param output_pdf_path: filename to save the PDF as
    :param data_dict: given dictionary mapping form field names to input
    """
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        for annotation in annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[PARENT_KEY][ANNOT_FIELD_KEY]:
                    key = annotation[PARENT_KEY][ANNOT_FIELD_KEY][1:-1]
                    if key in data_dict.keys():
                        if type(data_dict[key]) == bool:
                            if data_dict[key] == True:
                                annotation.update(pdfrw.PdfDict(
                                    AS=pdfrw.PdfName('Yes')))
                        else:
                            if key in ['Damage', 'Name']:
                                PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode('/Helvetica-BoldOblique 20.00 Tf 0 g')
                                annotation[PARENT_KEY].update(pdfrw.PdfDict(Q=1))
                            elif key in ['Guild', 'GunType', 'Rarity']:
                                # Updating the font to be Courier
                                PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode('/Helvetica-Bold 17.50 Tf 0 g')
                                annotation[PARENT_KEY].update(pdfrw.PdfDict(Q=1))
                            elif key in ['Element 1', 'Element 2', 'Element 3']:
                                # Updating the font to be Courier
                                PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode('/Helvetica-Bold 8.50 Tf 0 g')
                                annotation[PARENT_KEY].update(pdfrw.PdfDict(Q=1))
                            elif 'Hit' in key or 'Crit' in key:
                                # Updating the font to be Courier
                                PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode('/Helvetica-BoldOblique 15.00 Tf 255 g')
                                # annotation[PARENT_KEY].update(pdfrw.PdfDict(Q=1))
                            else:
                                # Updating the font to be Courier
                                PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode('/Helvetica-Bold 12.50 Tf 0 g')

                            annotation[PARENT_KEY].update({'/DA': PDF_TEXT_APPEARANCE})

                            # Adding in the value given
                            annotation.update(
                                pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                            )

                            # Change from fillable to static text
                            annotation[PARENT_KEY].update(pdfrw.PdfDict(Ff=1))

                            # Update the AP of this annotation to nothing
                            annotation[PARENT_KEY].update(pdfrw.PdfDict(AP=''))

    # Force form appearance to show and output PDF
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))  # NEW
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


def add_image_to_pdf(pdf_path, out_path, image, position):
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


def generate_gun_pdf(base_dir, output_name, gun, gun_images):
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
    elif gun.guild_info is not None:
        guild_str += "{:<15} {}: {}\n\n".format("(Guild)", gun.guild.title(), gun.guild_mod)

    # Construct element blocks
    element_strings = ['', '', '']
    if type(gun.element) == list:
        for idx, e in enumerate(gun.element):
            element_strings[idx] += e.title() + '\n'

    if type(gun.element) == str:
        element_strings[0] += gun.element.title()

    # Build up data dictionary to fill in PDF
    data_dict = {
        'Name': gun.name,
        "GunType": gun.type.title().replace('_', ' '),
        "Guild": gun.guild.title(),
        "Rarity": gun.rarity.title(),

        'Range': str(gun.range),
        'Damage': str(gun.damage),
        "Hit_Low": '{}'.format(gun.accuracy['2-7']['hits']),
        "Hit_Medium": '{}'.format(gun.accuracy['8-15']['hits']),
        "Hit_High": '{}'.format(gun.accuracy['16+']['hits']),
        "Crit_Low": '{}'.format(gun.accuracy['2-7']['crits']),
        "Crit_Medium": '{}'.format(gun.accuracy['8-15']['crits']),
        "Crit_High": '{}'.format(gun.accuracy['16+']['crits']),

        "Element 1": element_strings[0],
        "Element 2": element_strings[1],
        "Element 3": element_strings[2],

        "RedText": redtext_str,
        "Prefix": prefix_str,
        "GuildMod": guild_str,
        "ItemLevel": "Item Level: {}".format(gun.item_level)
    }

    # Fill the PDF with the given information
    fill_pdf(base_dir + 'resources/GunTemplate.pdf', base_dir + 'output/' + output_name + '_temp.pdf', data_dict)

    # Get a gun sample
    gun_images.sample_gun_image(gun.type, gun.guild)

    # Apply image to gun card
    position = {'page': 1, 'x0': 400, 'y0': 200, 'x1': 700, 'y1': 400}
    add_image_to_pdf(base_dir + 'output/' + output_name + '_temp.pdf',
                     base_dir + 'output/' + output_name + '.pdf',
                     base_dir + 'output/temporary_gun_image.png',
                     position)

    # Clean up temporary files
    os.remove(base_dir + "output/" + output_name + '_temp.pdf')
    os.remove(base_dir + "output/temporary_gun_image.png")


if __name__ == '__main__':
    # Parse arguments for generating a gun
    parser = argparse.ArgumentParser()

    parser.add_argument('--output', type=str, default="output", help='Name of the output PDF to use.')

    parser.add_argument('--name', type=str, default=None, help='Specify a given name for the gun')

    parser.add_argument('--prefix', type=str, default='True', choices=['True', 'False'],
                        help='Specify whether to roll for a prefix')

    parser.add_argument('--redtext', type=str, default='True', choices=['True', 'False'],
                        help='Specify whether to roll for a red text')

    parser.add_argument('--rarity', type=str, default=None,
                        choices=['random', 'common', 'uncommon', 'rare', 'epic', 'legendary'],
                        help='Specify a specific rarity')

    parser.add_argument('--rarity_element', type=str, default='False', choices=['True', 'False'],
                        help='Specify whether the rarity roll is elemental')

    parser.add_argument('--item_level', type=str, default=None,
                        choices=['1-6', '7-12', '13-18', '19-24', '25-30'],
                        help='Specify a specific item level')

    gun_type_choices = ['pistol', 'submachine_gun', 'shotgun', 'combat_rifle', 'sniper_rifle', 'rocket_launcher']
    parser.add_argument('--type', type=str, default=None, choices=gun_type_choices, help='Specify a specific item level')

    parser.add_argument('--guild', type=str, default=None,
                        choices=['random', 'alas!', 'skuldugger', 'dahlia', 'blackpowder', 'hyperius', 'feriore', 'torgue', 'stoker'],
                        help='Specify a specific guild')

    args = parser.parse_args()

    # Convert type to digits
    if args.type is not None:
        args.type = str(gun_type_choices.index(args.type) + 1)

    # Convert boolean params to boolean objects
    args.prefix = True if args.prefix == "True" else False
    args.redtext = True if args.redtext == "True" else False
    args.rarity_element = True if args.rarity_element == "True" else False

    # Load in the gun images dataset
    gun_images = GunImage()

    # Generate a gun
    gun = Gun(name=args.name, item_level=args.item_level,
              gun_type=args.type, gun_guild=args.guild, gun_rarity=args.rarity,
              rarity_element=args.rarity_element, prefix=args.prefix, redtext=args.redtext)
    print(gun.__str__())

    # Output a Form-filled PDF with the Gun parameters
    generate_gun_pdf(args.output, gun, gun_images)