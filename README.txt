scrape dbdbd and generate list of relevant genes, given a set of selected phenotypes

description of files
--------------------

scrape.py - scrape dbdb, store result in db/genes.csv (genes),
            db/phenotypes.csv (phenotypes), db/syndromes.csv (syndromes),
	    and db/list.csv (associations)

filter.py - generate result.csv from scraped data + selection.csv

util.py - utility functions

db/genes.csv - scraped genes

db/phenotypes.csv - scraped phenotypes

db/syndromes.csv - scraped syndromes

db/list.csv - scraped associations

selection.csv - list of relevant phenotypes

result.csv - generated list of relevant genes for selected phenotypes in selection.csv

gdoc.py - download selection.csv from google sheet (url put in gdoc.conf)

gdoc.conf - url to google document containing selected relevant phenotypes
