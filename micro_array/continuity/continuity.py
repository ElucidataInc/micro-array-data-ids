import GEOparse
import pandas as pd
import sys
import requests
import shutil
from datetime import datetime, timedelta
import tqdm
import os
from xml.etree import ElementTree
from ftplib import FTP
import re

REPO_ID = "9"
LAG_DAYS = 2
pdat = (datetime.today() - timedelta(days=LAG_DAYS)).strftime("%Y/%m/%d")

search_url  = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term="Expression+Profiling+by+Array"[DataSet Type]+AND+("Mus+musculus"[Organism]+OR+"Homo+sapiens"[Organism]+OR+"rattus norvegicus"[Organism])+AND+"{pdat}"[PDAT]&usehistory=y'
print(f"Searching using {search_url}")

search_r = requests.get(search_url)
search_tree = ElementTree.fromstring(search_r.content)

n_dsets = search_tree.find("Count").text
query_key = search_tree.find("QueryKey").text
webenv = search_tree.find("WebEnv").text

if int(n_dsets) == 0:
    print("No datasets returned in search results")
    sys.exit(0)

summary_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&version=2.0&query_key={query_key}&WebEnv={webenv}'
dset_r = requests.get(summary_url)
dset_tree = ElementTree.fromstring(dset_r.content)

to_process = []

for elem in dset_tree.iter():
    if elem.tag == "Accession":
        if elem.text.startswith("GSE"):
            to_process.append(elem.text)

print(f"to process list: {to_process}")
print(f"length-to process list: {len(to_process)}")

gse_gpl_list = []
data_not_public = []


def get_gse_object(gse_id):
    gseurl = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
    myurl = f"{gseurl}?targ=self&acc={gse_id}&form=text&view=brief"
    soft_data = requests.post(myurl)
    with open("response.txt", "w") as f:
        f.write(soft_data.text)

    gse_parse = GEOparse.parse_GSE(filepath = "response.txt")
    #os.remove("response.txt")
    return gse_parse


def is_dataset_public(gse_id):
    ftp = FTP('ftp.ncbi.nlm.nih.gov')
    ftp.login()
    try:
        range_subdir = re.sub(r"\d{1,3}$", "nnn", gse_id)
        ftp.cwd(f'geo/series/{range_subdir}/{gse_id}/matrix')
        return True
   
    except:
        return False


for gse_id in tqdm.tqdm(to_process):
    if not is_dataset_public(gse_id):
        data_not_public.append(gse_id)
        continue

    gse_parse = get_gse_object(gse_id)
    if len(gse_parse.metadata) == 0:
        data_not_public.append(gse_id)
        continue
    # except:
    #     print(f"{gse_id} - data is not public")
    #     data_not_public.append(gse_id)
    #     continue

    if 'SuperSeries of' in gse_parse.relations:
        for gse_sub in gse_parse.relations["SuperSeries of"]:
            gse_parse_sub = get_gse_object(gse_sub)
            for gpl_id in gse_parse_sub.metadata['platform_id']:
                gse_gpl_list.append((gse_id, gpl_id))
        continue

    for gpl_id in gse_parse.metadata['platform_id']:
        gse_gpl_list.append((gse_id, gpl_id))
    

if len(gse_gpl_list) != 0:
    run_df = pd.DataFrame(gse_gpl_list, columns=["gse_id", "gpl_id"])
    run_df["repo_id"] = REPO_ID
    print(run_df.head())
    print(f"Number of datasets : {run_df.shape[0] -1}")
    run_df.to_csv("daily_datasets.csv", index = False)

else:
    print("None of the datasets are public yet. Adding to not public csv")


if len(data_not_public) >0:
    not_public_df = pd.DataFrame(data_not_public, columns = ["gse_id"])
    not_public_df.to_csv("datasets_not_public.csv", index = False)

sys.exit(0)

