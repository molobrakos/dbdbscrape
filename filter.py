#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrape
from pandas import read_csv, merge


FILE_RESULT = "result.csv"
FILE_SELECTION = "selection.csv"


def make_list():

    selection = read_csv(FILE_SELECTION,
                         header=None, names=["phenotype"],
                         encoding="utf-8")

    phenos = scrape.fetch_phenotypes()
    assocs = scrape.fetch_associations()
    genes = scrape.fetch_genes()
    syndromes = scrape.fetch_syndromes()

    print("got %4d phenotypes" % len(phenos))
    print("got %4d genes" % len(genes))
    print("got %4d syndromes" % len(syndromes))
    print("got %4d associations" % len(assocs))
    print("got %4d selected phenotypes" % len(selection))

    # no duplicates in local data
    assert not phenos.duplicated().any()

    # no duplicates in list of selected phenotypes
    assert not selection.duplicated().any()

    # all selected phenotypes must exist in db
    assert set(selection["phenotype"]) < set(phenos["phenotype"])

    result = selection
    result = merge(result, assocs, on="phenotype", how="left")
    result = merge(result, phenos, on="phenotype", how="left")
    result = merge(result, genes, on="gene", how="left")
    result = merge(result, syndromes, on="syndrome", how="left")

    # pandas can't handle integer n/a
    result["gene_chromosome"] = result["gene_chromosome"].fillna(0).astype(int)
    
    # rearrange cols in suitable order
    result = result[['phenotype',
                     'gene',
                     'gene_chromosome',
                     'gene_inheritence',
                     'phenotype_name',
                     'syndrome',
                     'phenotype_description',
                     'phenotype_url',
                     'gene_url_ucsc',
                     'gene_url',
                     'gene_url_lynx',
                     'syndrome_synonyms',
                     'syndrome_inheritence',
                     'syndrome_url',
                     'syndrome_name',
                     'syndrome_features']]
    result.sort_values(["phenotype", "gene"], inplace=True)
    print("got %d relevant genes for %d selected phenotypes" %
          (len(result), len(selection)))
    result.to_csv(FILE_RESULT, encoding="utf-8", index=None)


if __name__ == "__main__":
    make_list()
