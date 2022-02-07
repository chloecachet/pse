"""
Copyright (c) 2021, Benjamin Fuller

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

import concurrent
import sys, os, math, asyncio, glob, numpy as np
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

from pathos.multiprocessing import ProcessingPool as Pool, cpu_count

from pse import multibasispredipe, prox_search, predipe

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))


def read_fvector(filePath):
    with open(filePath) as f:
        for line in f.readlines():
            temp_str = np.fromstring(line, sep=",")
            return [int(x) for x in temp_str]


def process_dataset():
    cwd = os.getcwd()
    # print(cwd)
    if os.path.exists(cwd + "//features//ND_proximity_irisR_features//"):
        feat_list = glob.glob(cwd + "//features//ND_proximity_irisR_features//*")
        # print(feat_list)
        nd_dataset = [read_fvector(x) for x in feat_list]
        return nd_dataset
    else:
        print("Notre-Dame dataset was not included in this repo for copyright reasons.")
        return


# Doing some basic testing
print("Testing Basic Multi-basis Predicate Functionality (n = 8)")
n = 8
group_name = 'MNT159'

x1 = [1, -1, 1, -1, 1, -1, 1, -1]
y1 = [1, 1, 1, 1, 1, 1, 1, 1]
y2 = [1, 5, 1, 1, 1, 1, 1, 1]
x2 = [0, 0, 0, 0, 0, 0, 0, 0]

print("Testing for sigma = 1")
barbosa = multibasispredipe.MultiBasesPredScheme(n, group_name)
barbosa.generate_keys()

ctx = barbosa.encrypt(x1)
tky1 = barbosa.keygen(y1)
tky2 = barbosa.keygen(y2)
ctzero = barbosa.encrypt(x2)

assert(multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctx, tky1, group_name))
assert(multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctzero, tky1))
assert(not multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctx, tky2))
print("Test passed.")


print("Testing for sigma = 4")
barbosa = multibasispredipe.MultiBasesPredScheme(n, group_name, False, 4)
barbosa.generate_keys()

ctx = barbosa.encrypt(x1)
tky1 = barbosa.keygen(y1)
tky2 = barbosa.keygen(y2)
ctzero = barbosa.encrypt(x2)

assert(multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctx, tky1, group_name))
assert(multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctzero, tky1))
assert(not multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctx, tky2))
print("Test passed.")


print("Testing for sigma = 3")
barbosa = multibasispredipe.MultiBasesPredScheme(n, group_name, False, 3)
barbosa.generate_keys()

ctx = barbosa.encrypt(x1)
tky1 = barbosa.keygen(y1)
tky2 = barbosa.keygen(y2)
ctzero = barbosa.encrypt(x2)

assert(multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctx, tky1, group_name))
assert(multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctzero, tky1))
assert(not multibasispredipe.MultiBasesPredScheme.decrypt(barbosa.getPublicParameters(), ctx, tky2))
print("Test passed.")

# print("Testing proximity search")
# print("Retrieving ND dataset ...")
# nd_dataset = process_dataset()
# vector_length = len(nd_dataset[0])
# database = prox_search.ProximitySearch(vector_length, predipe.BarbosaIPEScheme, group_name)
# print("Generating secret keys ...")
# database.generate_keys()
# database.deserialize_key("matrix.prox", "gen.prox")
# print("Encrypting data set ...")
# database.encrypt_dataset(nd_dataset)
# print(database.predicate_scheme.group.__str__)
# database.encrypt_dataset_parallel(nd_dataset)
# prox_search.ProximitySearch.augment_encrypt(vector_length, predipe.BarbosaIPEScheme, group_name, "matrix.prox", "gen.prox", database.public_parameters, nd_dataset)

# query_plain = nd_dataset[3]
# print("Generating query ...")
# query = database.generate_query(query_plain, 5)
#
# print("Running search ...")
# asyncio.run(database.search_parallel(query))
print("End test")
