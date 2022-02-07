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

"""
Implementation of Ahmad et al. Proximity Search Scheme 
"""

import concurrent
import sys, os, math, random, time, zlib, secrets, dill, threading, time, asyncio
from math import ceil
from charm.core.engine.util import objectToBytes, bytesToObject

# Path hack
sys.path.insert(0, os.path.abspath('charm'))
sys.path.insert(1, os.path.abspath('../charm'))

from subprocess import call, Popen, PIPE

from pathos.multiprocessing import ProcessingPool as Pool, cpu_count


class ProximitySearch():
    def __init__(self, n, predicate_scheme, group_name='MNT159', simulated=False):
        self.predicate_scheme = predicate_scheme
        self.predinstance = predicate_scheme(n + 1, group_name, simulated)
        self.public_parameters = None
        self.vector_length = n
        self.enc_data = None
        self.matrix_file = None
        self.generators_file = None
        self.group_name = group_name
        self.parallel = 0
        self.enc_data_size = 0
        self.num_records = 0

    def generate_keys(self):
        self.predinstance.generate_keys()
        self.public_parameters = self.predinstance.getPublicParameters()

    def serialize_key(self):
        return self.predinstance.serialize_key()

    def deserialize_key(self, matrix_str, generator_bytes):
        self.predinstance.deserialize_key(matrix_str, generator_bytes)
        self.public_parameters = self.predinstance.getPublicParameters()

    def read_key_from_file(self, matrix_filename, generator_filename):
        self.predinstance.read_key_from_file(matrix_filename, generator_filename)

    def write_key_to_file(self, matrix_filename, generator_filename):
        self.predinstance.write_key_to_file(matrix_filename, generator_filename)


    @staticmethod
    def augment_encrypt(n, predicate_scheme, group_name, matrix_str, generator_bytes, pp, vec_list, start_index,
                        end_index):
        prox_instance = ProximitySearch(n, predicate_scheme, group_name)
        prox_instance.deserialize_key(matrix_str, generator_bytes)
        prox_instance.public_parameters = pp
        prox_instance.encrypt_dataset(vec_list)

        # store encrypted data chunk in file ciphertexts_pid
        with open("ciphertexts_" + str(start_index) + "_" + str(end_index), "wb") as enc_file:
            enc_file.write(objectToBytes(prox_instance.enc_data, prox_instance.predinstance.group))
            enc_file.close()
            return os.stat("ciphertexts_" + str(start_index) + "_" + str(end_index)).st_size
        # TODO will need to augment this to store class identifier

    def encrypt_dataset_parallel(self, data_set):
        self.parallel = 1
        for data_item in data_set:
            if len(data_item) != self.vector_length:
                raise ValueError("Improper Vector Size")
        self.enc_data = {}

        processes = cpu_count()
        data_set_split = []
        data_set_len = len(data_set)
        self.num_records = data_set_len
        for j in range(processes):
            start = ceil(j * data_set_len / processes)
            end = ceil((j + 1) * data_set_len / processes)
            if end > data_set_len:
                end = data_set_len
            data_set_split.append((start, end, data_set[start:end]))
        total_data_size = 0
        (matrix_str, generator_bytes) = self.serialize_key()
        with Pool(processes) as p:
            with concurrent.futures.ProcessPoolExecutor(processes) as executor:
                future_list = {executor.submit(self.augment_encrypt, self.vector_length, self.predicate_scheme,
                                               self.group_name, matrix_str, generator_bytes,
                                               self.public_parameters, data_set_component, start, end)
                               for (start, end, data_set_component) in data_set_split
                               }
                for future in concurrent.futures.as_completed(future_list):
                    res = future.result()
                    if res is not None:
                        total_data_size = total_data_size + res
        self.enc_data_size = total_data_size

    def encrypt_dataset(self, data_set):
        for data_item in data_set:
            if len(data_item) != self.vector_length:
                raise ValueError("Improper Vector Size")
        self.enc_data = {}

        i = 0
        for x in data_set:
            x2 = [xi if xi == 1 else -1 for xi in x]
            x2.append(-1)
            self.enc_data[i] = self.predinstance.encrypt(x2)
            i = i + 1

    def generate_query(self, query, distance):
        encoded_query = [xi if xi == 1 else -1 for xi in query]
        query_set = []
        for i in range(distance + 1):
            temp_query = list(encoded_query)
            temp_query.append(self.vector_length - 2 * i)
            query_set.append(temp_query)

        # print("Query set is " + str(query_set))
        encrypted_query = []
        while (len(query_set) > 0):
            next_to_encode = secrets.randbelow(len(query_set))
            encrypted_query.append(self.predinstance.keygen(query_set[next_to_encode]))
            query_set.remove(query_set[next_to_encode])
        return encrypted_query

    @staticmethod
    def augment_search(n, predicate_scheme, group_name, matrix_str, generator_bytes, token_bytes, pp,
                       start_index, end_index):
        prox_scheme = ProximitySearch(n + 1, predicate_scheme, group_name)
        prox_scheme.deserialize_key(matrix_str, generator_bytes)
        prox_scheme.public_parameters = pp
        with open("ciphertexts_" + str(start_index) + "_" + str(end_index), "rb") as enc_file:
            prox_scheme.enc_data = bytesToObject(enc_file.read(), prox_scheme.predinstance.group)
            enc_file.close()
        token = bytesToObject(token_bytes, prox_scheme.predinstance.group)
        indices = prox_scheme.search(token)
        return [x+start_index for x in indices]

    def parallel_search(self, query):
        self.parallel = 1

        processes = cpu_count()
        data_set_split = []
        query_filename = "query"
        query_bytes = objectToBytes(query, self.predinstance.group)

        for j in range(processes):
            start = ceil(j * self.num_records / processes)
            end = ceil((j + 1) * self.num_records / processes)
            if end > self.num_records:
                end = self.num_records
            data_set_split.append((start, end))
        overall_return_list = []
        (matrix_str, generator_bytes) = self.serialize_key()
        with Pool(processes) as p:
            with concurrent.futures.ProcessPoolExecutor(processes) as executor:
                future_list = {
                    executor.submit(self.augment_search, self.vector_length, self.predicate_scheme, self.group_name,
                                    matrix_str, generator_bytes, query_bytes, self.public_parameters, start,
                                    end)
                    for (start, end) in data_set_split
                    }
                for future in concurrent.futures.as_completed(future_list):
                    res = future.result()
                    if res is not None and len(res) > 0:
                        overall_return_list = overall_return_list + res

        return overall_return_list

    def search(self, query):
        result_list = []
        for x in self.enc_data:
            index = None
            for subquery in query:
                if self.predinstance.decrypt(self.predinstance.getPublicParameters(), self.enc_data[x], subquery, self.group_name):
                    index = int(x)
                    break
            if index is not None:
                result_list.append(index)
        return result_list

    @staticmethod
    def get_ct_size(ct):
        ct_sizeinbytes = 0
        for elem in ct:
            elem_sizeinbytes = 0
            # extract integers from elem
            str_rep = ''.join(filter(lambda c: c == ' ' or c.isdigit(), str(elem)))
            delim_size = len(str(elem)) - len(str_rep)  # number of delimiter characters
            elem_sizeinbytes += delim_size
            L = [int(s) for s in str_rep.split()]
            for x in L:
                intsize = int(math.ceil(math.log2(x) / 8))
                elem_sizeinbytes += intsize
            ct_sizeinbytes += elem_sizeinbytes
        return ct_sizeinbytes

    def get_database_size(self):
        if self.parallel is 0:
            running_total = 0
            for x in self.enc_data:
                running_total += self.get_ct_size(self.enc_data[x])
            return running_total
        else:
            return self.enc_data_size

    def get_seckey_size(self):
        return self.predinstance.get_seckey_size()

