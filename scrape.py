#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
scrape data from dbd (developmental brain disorders database)
at https://www.dbdb.urmc.rochester.edu/phenotypes/list

some workarounds to get access to this (esoteric) web service:
- the ssl certificate does not verify, must add verify=False
- no structured output (json/xml), only html
- must use Accept: text/html
- frequent timeouts
- drops connection, no keep alive
- the database seems to be uploaded to github at
  https://github.com/Paciorkowski-Lab/DBDB/blob/master/DBDB_25Nov2014.sql
  but we're scraping the "web service" anyway since we won't know how
  recent the github dump is compared to the web service
"""


import re
from urlparse import urljoin
from util import load_doc, whitelisted
from pandas import DataFrame, read_csv
from os.path import basename, join


DBDB_URL = "https://www.dbdb.urmc.rochester.edu"
URL_LYNX = "http://lynx.ci.uchicago.edu/gene/?geneid=%s"
URL_UCSC = "http://genome.ucsc.edu/cgi-bin/hgTracks?" \
           "org=human&db=hg19&singleSearch=knownCanonical&position=%s"
DIR_DB   = "db"  # where to put database mirror

def dbdb_load(url):
    doc = load_doc(url,
                   verify=False,
                   headers={"Accept": "text/html"})
    if not doc:
        print("failed to load document, exiting")
        exit(-1)
    return doc


def fetch(resource, extractor):
    fname = join(DIR_DB, "%s.csv" % whitelisted(basename(resource)))
    try:
        return read_csv(fname)
    except IOError:
        pass

    def filter_id(s):
        return s.replace("---", "").replace(":", "").strip()

    pseudo_rest = "/" not in resource
    if pseudo_rest:
        url = urljoin(DBDB_URL, "rest/%s" % resource)
        doc = dbdb_load(url)
        links = doc.items = doc.find_all("a")
        items = [(filter_id(link.previous_element),
                  link["href"]) for link in links]
        items = map(extractor, items)
    else:
        url = urljoin(DBDB_URL, resource)
        doc = dbdb_load(url)
        items = extractor(doc)
    result = DataFrame(items)
    result.to_csv(fname, encoding="utf-8", index=None)
    return result


def extract_pheno((phenotype_id, url)):
    doc = dbdb_load(url)
    name = doc.select("span.pheno h2")[0].text
    desc = doc.select("tr td")[3].text
    return {"phenotype": phenotype_id,
            "phenotype_name": name,
            "phenotype_description": desc,
            "phenotype_url": url}


def extract_syndrome((syndrome_id, url)):
    doc = dbdb_load(url)
    name = doc.find("span", "synd").text

    def get_item(what):
        elm = doc.find(text=what)
        return elm.find_next().text if elm else ""

    synonyms = get_item("Synonyms")
    features = get_item("Cardinal Features")
    inheritance = get_item("Inheritance")

    return {"syndrome": syndrome_id,
            "syndrome_name": name,
            "syndrome_synonyms": synonyms,
            "syndrome_features": features,
            "syndrome_inheritence": inheritance,
            "syndrome_url": url}


def extract_gene((gene_id, url)):
    return {"gene": gene_id,
            "gene_url": url,
            "gene_url_lynx": URL_LYNX % gene_id,
            "gene_url_ucsc": URL_UCSC % gene_id}


def extract_assocs(doc):
    def extract_assoc(tr):
        tds = tr.select("td")
        gene = tds[0].text.strip()
        inheritance = tds[1].text.strip()
        phenotype = re.findall("phenotypes/(.*)", tds[2].a["href"])[0]
        syndrome = re.findall("syndromes/(.*)", tds[3].a["href"])[0]
        loc = tds[4].text.strip()
        return {"gene": gene,
                "phenotype": phenotype,
                "syndrome": syndrome,
                "gene_inheritence": inheritance,
                "gene_chromosome": loc}
    return map(extract_assoc, doc.select("table.tablesorter tr")[1:])


def fetch_phenotypes():
    return fetch("phenotypes", extract_pheno)


def fetch_genes():
    return fetch("genes", extract_gene)


def fetch_syndromes():
    return fetch("syndromes", extract_syndrome)


def fetch_associations():
    return fetch("associations/list", extract_assocs)


def scrape():
    phenos = fetch_phenotypes()
    genes = fetch_genes()
    syndromes = fetch_syndromes()
    assocs = fetch_associations()

    print("got %4d phenotypes" % len(phenos))
    print("got %4d genes" % len(genes))
    print("got %4d syndromes" % len(syndromes))
    print("got %4d associations" % len(assocs))


if __name__ == "__main__":
    scrape()
