<p align="center"><img src="https://user-images.githubusercontent.com/32918812/163755438-a98ff76f-7ce8-4ff5-978d-a4a3ef8b138e.png" /></p>

<hr>

LootGenerator is a local application to handle Gun and Lootsplosion generation in the Nerdvana TTRPG, <a href="https://nerdvanagames.myshopify.com/">Bunkers & Badasses</a>. Additionally, it includes transcribed roll tables from the source book for all item types in the game.
 
## Running:
Currently this program is a PyQT GUI application in which the user can specify specific gun attributes to roll with. 

This will save a local PDF that can be printed off or sent to players.
![Screenshot 2022-05-16 013155](https://user-images.githubusercontent.com/32918812/168525681-b73cec7f-c90d-48fb-9bca-ecc3bc9bc6d0.png)

## Note on PDF Viewers
The local version of this application requires a PDFViewer capable of form/annotation rendering in order to view the generated text on the Gun Card. PDF Viewers are all over the place when it comes to support for this and it cannot be guaranteed LootGenerator will work with a given viewer. Alternative solutions were tried for rendering (e.g. pdf2image conversion, pdfjs, local chromium server), but no universal solution works. Without a full rewrite, this solution will have to suffice for now. We apologize for the inconvenience!

Here is a list of ones that work and don't work thus far from personal testing. Please put up an issue if you use one of the untested versions!

<b>Working:</b> Acrobat Reader DC, 

<b>Not Working:</b> Foxit PDF (under Safe Mode), Browser PDFs (Brave, Chromium, etc), MacOS

<b>Untested</b>: Slim Reader, Nitro Reader, PDF Viewer Pro, Xodo PDF Reader, ...

## Folder Layout:
```
  BnB-LootGenerator/
  │
  ├── local_app.py      - Entrypoint for the PyQT local application
  ├── requirements      - Automatically installs needed pypi packages
  |
  ├── classes/
  │   ├── Gun.py        - Gun generation script
  │   ├── GunImage.py   - Image filtering script
  │   ├── GunPDF.py     - PDF generation script
  │   ├── ...           - Other items follow the same scheme
  ├── resources/
  │   ├── chests/       - Tables for chests, caches, etc
  │   ├── elements/     - Tables for element rolling
  │   ├── guns/         - Tables dedicated to gun generation
  │   ├── images/       - Tables that have URL PNG links to gun art from all Borderland games
  │   ├── misc/         - Holds the tables for misc objects (shields, grenades, etc)
  ├── tests/
```
  
## Custom Additions:
LootGenerator allows for easily adding customized rules/mods to expand the generation options. As the generation script dynamically parses
the JSON files on runtime, one just needs to add a new item to the relevant JSON file in the resources/ folder.

#### Examples of custom parts include:
<ul>
    <li>Elements (Type/Rolling Tiers)</li>
    <li>Guilds</li>
    <li>Gun Types</li>
    <li>Gun Stats</li>
    <li>Gun Prefixes</li>
    <li>Gun Images</li>
    <li>Red Text Mods</li>
</ul>

#### Instructions for adding:
For example, to add a new Guild, add a new JSON item to the "resources/guild.json" file in line to the
attributes of the others.

Adding an item to the JSON:

![adding_to_json](https://user-images.githubusercontent.com/32918812/163227008-68b1253e-3fa5-4602-bc8d-35cf4c4bfb91.png)

## TO-DO:
There are still a number of features in the works of being implemented. This includes the primary goal of outputting full loot generation tables
for encounters given a Badass Rank or type of Container (cache, disk chest, etc).

These are the components to be fleshed out yet (we're welcome to take contributions for these!):
<ul>
      <li><b> Containers</b>: Roll tables for cache, cache size, dice chests, and unassuming chests need to be input. As well, a class that handles rolling and providing function calls to relevant classes is needed.</li>
</ul>

## Note on Anti-Virus Catching
It is a common occurance that anti-viruses mistakenly flag Python executable programs that were compiled with PyInstaller as malicious software. We have applied for detection reviews for a number of these companies in order to get whitelisted. More information on this can be found <a href="https://github.com/hankhank10/false-positive-malware-reporting">here</a>.

## Issues and Contributions
Please feel free to put up any issues that are found or enhancements that would improve this work. As well, please feel welcome to put up PRs for any improvements that you can do!

## Credit
This tool is an unofficial automated tool for the Nerdvana TTRPG, <a href="https://nerdvanagames.myshopify.com/">Bunkers & Badasses</a>.

Gun art images are used from the Borderlands <a href="https://www.lootlemon.com/db/borderlands-3/weapons">Lootlemon</a> and images displayed are URL links to their hosted images.

All credit for source material and gun images belongs to Nerdvana and GearBox Software.

The chest design in our icon comes from Victor Escorsin, available <a href="https://thenounproject.com/icon/chest-7173/">here</a>. 

This icon is available as a sample icon on Adobe Spark's Logo Maker under the CC License.
