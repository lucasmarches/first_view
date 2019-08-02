# first_view
Automated reader of the Brazilian Official Diary created by Lucas Marchesini Palma as his final project for a MSc of Computational and Data Journalism at Cardiff University.

The code is a Django application that scraps the Brazilian Official Diary of the Union and look for a set of information in it.

The scraping routines are in the folder results, in the views.py file. It require a set of databases to work. Their implementation are in the file models in the same folder.

The folder Homepage is a django application that creates the landing page for the website. It also contain the static files used in the website, such as javascript scripts and HTML templates.
