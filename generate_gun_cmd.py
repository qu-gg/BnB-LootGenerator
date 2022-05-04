"""
@file generate_gun_cmd.py
@author Ryan Missel

Command line based script for users to generate guns and get a PDF of the BnB Card Design
filled out by the gun attributes that are generated.

Takes in user-input on specific gun features to choose
"""
import os
import fitz
import pdf2image
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
    appearances = {
        "Damage": ('/Helvetica-BoldOblique 20.00 Tf 0 g', 1),
        "Name": ('/Helvetica-BoldOblique 25.00 Tf 0 g', 1),

        "Guild": ('/Helvetica-Bold 17.50 Tf 0 g', 1),
        "GunType": ('/Helvetica-Bold 17.50 Tf 0 g', 1),
        "Rarity": ('/Helvetica-Bold 15.00 Tf 0 g', 1),

        "ElementBonus": ('/Helvetica-Bold 13.00 Tf 0 g', 1),

        "Hit": ('/Helvetica-Bold 15.00 Tf 255 g', 0),
        "Crit": ('/Helvetica-Bold 15.00 Tf 255 g', 0),
        "Range": ('/Helvetica-Bold 25.00 Tf 0 g', 0),

        "RedText": ('/Helvetica-Bold 13.00 Tf 0 g', 0),
        "Prefix": ('/Helvetica-Bold 13.00 Tf 0 g', 0),
        "GuildMod": ('/Helvetica-Bold 13.00 Tf 0 g', 0),
    }

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
                            # Get the appearance string
                            if 'Hit' in key or 'Crit' in key:
                                display_string, q_value = appearances.get(key.split('_')[0])
                            else:
                                display_string, q_value = appearances.get(key, ('/Helvetica-Bold 12.50 Tf 0 g', 0))

                            # Encode and update DisplayAppearance
                            PDF_TEXT_APPEARANCE = pdfrw.objects.pdfstring.PdfString.encode(display_string)
                            annotation[PARENT_KEY].update({'/DA': PDF_TEXT_APPEARANCE})

                            # Center text if given
                            if q_value == 1:
                                annotation[PARENT_KEY].update(pdfrw.PdfDict(Q=q_value))

                            # Adding in the value given
                            annotation.update(
                                pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                            )

                            # Change from fillable to static text
                            annotation[PARENT_KEY].update(pdfrw.PdfDict(Ff=1))
                            annotation.update(pdfrw.PdfDict(Ff=1))

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


def generate_gun_pdf(base_dir, output_name, gun, gun_images, rarity_border):
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
    fill_pdf(base_dir + 'resources/GunWhiteTemplate.pdf', base_dir + 'output/' + output_name + '_temp.pdf', data_dict)

    # Get a gun sample and apply a colored border depending
    if rarity_border is True:
        gun_images.sample_gun_image(gun.type, gun.guild, rarity=gun.rarity)
    else:
        gun_images.sample_gun_image(gun.type, gun.guild, None)

    # Apply gun art to gun card
    position = {'page': 1, 'x0': 350, 'y0': 150, 'x1': 750, 'y1': 400}
    add_image_to_pdf(base_dir + 'output/' + output_name + '_temp.pdf',
                     base_dir + 'output/' + output_name + '_temp2.pdf',
                     base_dir + 'output/temporary_gun_image.png',
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
    add_image_to_pdf(base_dir + 'output/' + output_name + '_temp2.pdf',
                     base_dir + 'output/' + output_name + '_temp3.pdf',
                     base_dir + 'resources/images/gun_icons/{}'.format(gun_icon_paths.get(gun.type)),
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
    add_image_to_pdf(base_dir + 'output/' + output_name + '_temp3.pdf',
                     base_dir + 'output/' + output_name + '_temp4.pdf',
                     base_dir + 'resources/images/guild_icons/{}'.format(guild_icon_paths.get(gun.guild)),
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
    add_image_to_pdf(base_dir + 'output/' + output_name + '_temp4.pdf',
                     base_dir + 'output/' + output_name + '_temp5.pdf',
                     base_dir + 'resources/images/die_icons/{}'.format(die_icon_paths.get(die_type)),
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
        os.rename(base_dir + 'output/' + output_name + '_temp5.pdf', base_dir + 'output/' + output_name + '.pdf')

    # Otherwise add the element icon
    else:
        position = {'page': 1, 'x0': 60, 'y0': 440, 'x1': 110, 'y1': 470}
        add_image_to_pdf(base_dir + 'output/' + output_name + '_temp5.pdf',
                         base_dir + 'output/' + output_name + '_temp6.pdf',
                         base_dir + 'resources/images/element_icons/{}'.format(element_icon_paths.get(element[0])),
                         position)
        os.remove(base_dir + "output/" + output_name + '_temp5.pdf')

        # In the event that there are 3 elements, add the third element as a separate icon below
        if len(element) == 2:
            position = {'page': 1, 'x0': 60, 'y0': 480, 'x1': 110, 'y1': 510}
            add_image_to_pdf(base_dir + 'output/' + output_name + '_temp6.pdf',
                             base_dir + 'output/' + output_name + '.pdf',
                             base_dir + 'resources/images/element_icons/{}'.format(element_icon_paths.get(element[1])),
                             position)
            os.remove(base_dir + "output/" + output_name + '_temp6.pdf')

        # Otherwise just rename to the final PDF
        else:
            os.rename(base_dir + 'output/' + output_name + '_temp6.pdf', base_dir + 'output/' + output_name + '.pdf')

    # Clean up temporary files
    os.remove(base_dir + "output/" + output_name + '_temp.pdf')
    os.remove(base_dir + "output/" + output_name + '_temp2.pdf')
    os.remove(base_dir + "output/" + output_name + '_temp3.pdf')
    os.remove(base_dir + "output/" + output_name + '_temp4.pdf')
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
    gun_images = GunImage("")

    # Generate a gun
    gun = Gun("", name=args.name, item_level=args.item_level,
              gun_type=args.type, gun_guild=args.guild, gun_rarity=args.rarity,
              rarity_element=args.rarity_element, prefix=args.prefix, redtext=args.redtext)
    print(gun.__str__())

    # Output a Form-filled PDF with the Gun parameters
    generate_gun_pdf("", args.output, gun, gun_images)