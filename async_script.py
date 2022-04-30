r"""
Parte 1
- Pegar pasta por pasta do diretório 'data'
- Filtar os arquivos que contém 'final_protein' e 'final_peptide'
- Do arquivo 'final_protein' pegar os campos 'protein.Entry' e 'protein.score'
- Do arquivo 'final_peptide' pegar os campos 'peptide.seq'
- O número do spot é dado por 'MARIA60_(\d{3})LX_IA' no nome do diretório
"""
from collections import namedtuple
from asyncio import get_event_loop, gather, sleep
from contextlib import contextmanager
from functools import reduce
from operator import add
from os import listdir, chdir, getcwd
from re import compile

from pandas import concat, read_csv
from httpx import AsyncClient
from bs4 import BeautifulSoup

PATH = 'data'
FILE = 'tabela.csv'

csv_data = namedtuple('CSV_DATA', 'spot entry score')
Protein = namedtuple('Protein', 'spot access gene protein pi_mw score')
exp_spot = compile(r'\w+_(\d{0,3})(LX_|_)\w+')
exp_uniprot = compile(r'UniProtKB\s-\s(\w+)\n')
exp_expasy = compile(r'Theoretical pI: (\d+\.\d+)')

file = open(FILE, 'w')
file.write('SPOT ID;Access;GENE SYMBOL;PROTEIN;pI/MW(kDa);SCORE\n')


@contextmanager
def cd(path):
    old_path = getcwd()
    chdir(PATH + '/' + path)
    yield
    chdir(old_path)


def filter_files(path):
    return [
        read_csv(file) for file in sorted(listdir('.'))
        if 'protein' in file or 'peptide' in file
    ]


def filter_one(path):
    return [
        read_csv(file) for file in listdir('.')
        if 'protein' in file
    ][0]


def merge_csvs(csv1, csv2):
    return concat([csv1, csv2])


async def download_data(protein_code):
    print(protein_code)
    async with AsyncClient() as client:
        try:
            uniprot = await client.get(
                f'https://www.uniprot.org/uniprot/?query={protein_code.entry}&sort=score',
                timeout=None
            )
            await sleep(.1)
            print('uniprot', protein_code)

            uniprot_soup = BeautifulSoup(
                uniprot.content.decode(), 'html.parser'
            )
            uniprot_code = uniprot_soup.find('h2', class_='page-title')
            uniprot_code = exp_uniprot.match(uniprot_code.text).group(1)

            uniprot_name = uniprot_soup.find(
                'div', class_='entry-overview-content'
            )
            uniprot_gene = uniprot_soup.find(
                'div', attrs={'id': 'content-gene'}
            )
            uniprot_isoform = uniprot_soup.find(
                'div', class_='sequence-isoform-rightcol'
            )
            uniprot_mass = uniprot_isoform.find_all('span')[3]

            expasy = await client.get(
                f'https://web.expasy.org/cgi-bin/compute_pi/pi_tool1?{uniprot_code}@noft@average',
                timeout=None
            )
            print('expasy', protein_code)
            await sleep(.1)
            expasy_soup = BeautifulSoup(expasy.content.decode(), 'html.parser')
            expasy_body = expasy_soup.find('div', attrs={'id': 'sib_body'})
            expasy_pi = expasy_body.find_all('p')[-1]

            p = Protein(
                protein_code.spot,
                protein_code.entry,
                uniprot_gene.text,
                uniprot_name.text,
                f'{exp_expasy.match(expasy_pi.text).group(1)}/{uniprot_mass.text.replace(",", ".")}',
                protein_code.score
            )
            await sleep(1)
            return p
        except AttributeError as e:
            print('==============================ERRRRRO========')
            print(e)
            print(protein_code)
            print('=============================================')


async def main():
    requests = []
    results = []

    for path in listdir(PATH):
        spot = int(exp_spot.match(path).group(1))
        with cd(path):
            csv = filter_one(path)
            data = csv[['protein.Entry', 'protein.score']].to_dict()

            for entry, score in zip(
                    data['protein.Entry'].values(),
                    data['protein.score'].values()
            ):
                if 'reverse' not in entry.lower():
                    requests.append(
                        download_data(
                            csv_data(spot, entry, score)
                        )
                    )
    print(len(requests))
    for reqs in [requests[i: i + 10] for i in range(0, len(requests), 10)]:
        partial = await gather(*reqs)
        results.append(partial)
    return results


if __name__ == '__main__':
    loop = get_event_loop()
    for protein in reduce(add, loop.run_until_complete(main())):
        file.write(';'.join(str(x) for x in protein) + '\n')
        file.close()
