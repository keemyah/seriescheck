#!/bin/bash
mkdir -p data
curl -o data/title.basics.tsv.gz https://datasets.imdbws.com/title.basics.tsv.gz
curl -o data/title.ratings.tsv.gz https://datasets.imdbws.com/title.ratings.tsv.gz
