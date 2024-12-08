<p align="center"><img src="https://user-images.githubusercontent.com/32918812/163755438-a98ff76f-7ce8-4ff5-978d-a4a3ef8b138e.png" /></p>

<hr>

LootGenerator is a local application to handle Gun and Lootsplosion generation in the Nerdvana TTRPG, <a href="https://nerdvanagames.myshopify.com/">Bunkers & Badasses</a>. Additionally, it includes transcribed roll tables from the source book for all item types in the game.
 
## Running:
Currently this program is a PyQT GUI application in which the user can specify specific gun attributes to roll with. 

<p align='center'><img src="https://user-images.githubusercontent.com/32918812/205549787-9d2d62f0-1d68-4fb3-b1bb-f5560d40661a.png" alt="gunFront" /></p>
<p align='center'>Fig 1. Front view of the 2-Sided Gun Card.</p>

<p align='center'><img src="https://user-images.githubusercontent.com/32918812/205549744-c5211acc-f243-4d66-99bc-f2cdca238f14.png" alt="gunBack" /></p>
<p align='center'>Fig 2. Back/Details view of the 2-Sided Gun Card.</p>

<p align='center'><img src="https://user-images.githubusercontent.com/32918812/183753821-ea56de4d-95e8-4f12-91a8-72dd2814b4f2.png" alt="exampleCard" /></p>
<p align='center'>Fig 3. Front/Back of a printed card.</p>

## Note on PDF Viewers
The local version of this application requires a PDFViewer capable of form/annotation rendering in order to view the generated text on the Gun Card. PDF Viewers are all over the place when it comes to support for this and it cannot be guaranteed LootGenerator will work with a given viewer. Alternative solutions were tried for rendering (e.g. pdf2image conversion, pdfjs, local chromium server), but no universal solution works. Without a full rewrite, this solution will have to suffice for now. We apologize for the inconvenience!

Here is a list of ones that work and don't work thus far from personal testing. Please put up an issue if you use one of the untested versions!

<b>Working:</b> Acrobat Reader DC, 

<b>Not Working:</b> Foxit PDF (under Safe Mode), Browser PDFs (Brave, Chromium, etc), MacOS

<b>Untested</b>: Slim Reader, Nitro Reader, PDF Viewer Pro, Xodo PDF Reader, ...

## PDF Filesize + Compression
~~By default the size of the output PDFs will be rather large (e.g. 40MB). This is due to how layer stacking is performed~~
~~in the PDF graph. No pure-Python libraries have the ability to perform compression with annotation and most external~~
~~programs are unable to preserve annotations.~~

~~However I found that QPDF (https://github.com/qpdf/qpdf/releases/tag/v11.1.1) is able to do this. As such, if QPDF 11.1.1~~
~~is installed and in <code>C:/Program Files/</code>, the PDF files will be automatically compressed (40MB -> 250KB!). The standard~~
~~installer package to grab is <code>qpdf-11.1.1-mingw64.exe</code> for Windows 10 users.~~

Resolved using pikepdf, a Python library based on QPDF. If compression fails for any reason, you should still have your PDF file, but still with the large file size due to layer stacking and get a message alerting you that it failed to compress.

<p align='center'><img src="https://user-images.githubusercontent.com/32918812/197358506-e0b39fd4-befa-40a2-a122-022473fdabdb.png" alt="gunBack" /></p>
<p align='center'>Fig 4. Compression gained by QPDF.</p>

## FoundryVTT Support
This LootGenerator has support for outputting files to import into Eronth's 
<a href="https://github.com/eronth/bunkers-and-badasses">BnB FoundryVTT</a> system!
There is a checkbox in the program that outputs a .JSON file that the <code>Import Data</code> function on Items recognizes. 
The files are stored in <code>api/foundryVTT/outputs/</code>.

<p align='center'><img src="https://user-images.githubusercontent.com/32918812/197358814-5445cb01-0b36-42bc-b773-5d57d9df701b.png" alt="gunBack" /></p>
<p align='center'>Fig 5. Process of importing items into FoundryVTT.</p>

## Folder Layout:
```
  BnB-LootGenerator/
  │
  ├── main.py           - Entrypoint for the PyQT local application
  ├── requirements      - Automatically installs needed pypi packages
  │
  ├── api/
  │   └── foundryVTT/   - FoundryVTT folder and output files
  ├── app/
  │   ├── GunTab.py     - PyQt tab dedicated to Gun display
  │   └── ...           - Tabs for relics, shields, etc.
  ├── classes/
  │   ├── Gun.py        - Gun generation script
  │   ├── GunImage.py   - Image filtering script
  │   ├── GunPDF.py     - PDF generation script
  │   └── ...           - Other items follow the same scheme
  ├── output/
  │   ├── grenades/     - Folder to hold generated grenades
  │   └── ...           - Other folders for other items
  ├── resources/
  │   ├── chests/       - Tables for chests, caches, etc
  │   ├── elements/     - Tables for element rolling
  │   ├── guns/         - Tables dedicated to gun generation
  │   ├── images/       - Tables that have URL PNG links to gun art from all Borderland games
  │   └── misc/         - Holds the tables for misc objects (shields, grenades, etc)
  │── tests/
  └────
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

### Damage Balance Tables
The alternative damage balancing sheets are homebrew systems provided with permission by other community members.

Here are the direct links to their works:

- <a href="https://docs.google.com/file/d/14eFUSu1MnjKoJIaddZCy6NOh8euosf3V/edit?filetype=msexcel">McCoby's</a>
- <a href="https://docs.google.com/spreadsheets/d/1rw7bS7kXxMOezy2Dy_7JQaDRbiJE0CFSKmYyoEcbg5E/edit#gid=0">RobMWJ's</a>

### Materials
This tool is an unofficial automated tool for the Nerdvana TTRPG, <a href="https://nerdvanagames.myshopify.com/">Bunkers & Badasses</a>.

Gun art images are used from the Borderlands <a href="https://www.lootlemon.com/db/borderlands-3/weapons">Lootlemon</a> and images displayed are URL links to their hosted images.

All credit for source material and gun images belongs to Nerdvana and GearBox Software.

The chest design in our icon comes from Victor Escorsin, available <a href="https://thenounproject.com/icon/chest-7173/">here</a>. 

This icon is available as a sample icon on Adobe Spark's Logo Maker under the CC License.
