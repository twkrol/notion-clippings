# notion-clippings
Import Kindle clippings into a Notion's collection

# When would you like to use this tool
In case you would like to import your Kindle highlights collection into Notion for further use.

# Getting started
First you have to create a database in Notion with at least the following columns:
* **Title** of type Title (you can rename the initial column Name)
* **Status** of type Select
* **Text** of type Text
* **Authors** of type Text
* **Date** of type Date
* **Location** of type Text

Next find path to your Kindle 'My Clippins.txt' file (you can put it into the app folder below)

Then follow these steps for pipenv:
1. Download/clone this python app
2. Open virtualenv: <code>pipenv shell</code>
3. Install referenced libraries: <code>pipenv install</code>
4. Copy <code>config.ini.example</code> to <code>config.ini</code>
5. Edit config.ini (your api_token and collection_page_url are mandatory)
6. Run application: <code>python start.py</code>

# Disclaimer
This tool can, and probably will modify your Notion data! It was not extensivelly tested, so any errors may occur and you may lost your data.
For the first time run it on a simple demo collection to avoid any unwanted data modifications.
I'm not responsible for any damages it may cause.
*You have been warned*

