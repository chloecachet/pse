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

import sys, os, math, argparse
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

from pse import predipe, prox_search, multibasispredipe

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Benchmarking of Proximity Search Schemes.')
    parser.add_argument('--matrix_file', '-mf', nargs='*', help='The file for the matrices')
    parser.add_argument('--generator_file', '-gf', nargs='*', help='The file for the group generators')
    parser.add_argument('--save', '-s', const=1, type=int, nargs='?', default=0,
                        help='Write a secret key to file and quit')
    parser.add_argument('--load', '-l', const=1, type=int, nargs='?', default=0,
                        help='Load secret key from a file')
    parser.add_argument('--benchmark', '-b', const=1, type=int, nargs='?',
                        default=0, help='Perform Full benchmarking')
    parser.add_argument('--vector_length', '-v', const=1, type=int, nargs='?', default=64,
                        help='Specify the length of vectors for testing')
    args = vars(parser.parse_args())

    vector_length = args['vector_length']

    group_name = 'MNT159'
    barbosa = predipe.BarbosaIPEScheme(n=vector_length)
    database = prox_search.ProximitySearch(vector_length, predipe.BarbosaIPEScheme, group_name)

    if(args['save'] and args['matrix_file'] and args['generator_file']):
        barbosa.generate_keys()
        barbosa.serialize_key(args['matrix_file'][0]+'pred', args['generator_file'][0]+'pred')

        database.generate_keys()
        database.serialize_key(args['matrix_file'][0]+'prox', args['generator_file'][0]+'prox')


    elif(args['load'] and args['matrix_file'] and args['generator_file']):
        barbosa.deserialize_key(args['matrix_file'][0]+'pred', args['generator_file'][0]+'pred')
        database.deserialize_key(args['matrix_file'][0]+'prox', args['generator_file'][0]+'prox')
    else:
        barbosa.generate_keys()
        database.generate_keys()

    if vector_length == 4:
        print("Testing Basic Predicate Functionality")
        x1=[1, -1, -1, 1]
        ctx = barbosa.encrypt(x1)
        y1=[1, 1, 1, 1]
        y2=[1, 5, 1, -3]
        tky1 = barbosa.keygen(y1)
        tky2 = barbosa.keygen(y2)
        x2=[0, 0, 0, 0]
        ctzero = barbosa.encrypt(x2)
        assert(predipe.BarbosaIPEScheme.decrypt(barbosa.getPublicParameters(), ctzero, tky1))
        assert(not predipe.BarbosaIPEScheme.decrypt(barbosa.getPublicParameters(), ctx, tky2))
        assert(predipe.BarbosaIPEScheme.decrypt(barbosa.getPublicParameters(), ctx, tky1, group_name))


        print("Testing Proximity Search")
        data = [[0, 1, 0, 1], [1, 0, 1, 0]]
        database.encrypt_dataset(data)
        print("Size of DB "+str(database.get_database_size()))
        print("Size of Secret Key "+str(database.get_seckey_size()))
        query = [0,1,0,0]
        encrypted_query = database.generate_query(query, 1)
        assert(len(encrypted_query)==2)
        relevant_indices = database.search(encrypted_query)
        assert(len(relevant_indices)==1 and relevant_indices[0] == 0)
        encrypted_query = database.generate_query(query, 0)
        assert (len(encrypted_query) == 1)
        relevant_indices = database.search(encrypted_query)
        assert (len(relevant_indices) == 0)



        print("Testing multi basis scheme")
        x1 = [1, -1, -1, 1]
        x2 = [0, 0, 0, 0]
        y1 = [1, 1, 1, 1]
        y2 = [1, 5, 1, -3]


        # multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=1)
        # multi_scheme.generate_keys()
        # ctx = multi_scheme.encrypt(x1)
        # tky1 = multi_scheme.keygen(y1)
        # tky2 = multi_scheme.keygen(y2)
        # ctzero = multi_scheme.encrypt(x2)
        #
        # assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1))
        # assert (not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2))
        # assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky1, group_name))
        #
        # multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=2)
        # multi_scheme.generate_keys()
        # ctx = multi_scheme.encrypt(x1)
        # tky1 = multi_scheme.keygen(y1)
        # tky2 = multi_scheme.keygen(y2)
        # ctzero = multi_scheme.encrypt(x2)
        #
        # assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1))
        # assert (not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2))
        # assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky1, group_name))

        for i in [1, 2, 3, 4, 6, 12]:
            multi_scheme = multibasispredipe.MultiBasesPredScheme(n=12, group_name=group_name, num_bases=6)
            multi_scheme.generate_keys()
            ctx = multi_scheme.encrypt([1, 1, 1,  1, 1,  1, 1, -1, 1,  1, 1,  1])
            tky = multi_scheme.keygen([1, -1, 1, -1, 1, -1, 1,  1, 1, -1, 1, -1])
            assert (multi_scheme.fake_decrypt(multi_scheme.getPublicParameters(), ctx, tky))

        # multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=4)
        # multi_scheme.generate_keys()
        # ctx = multi_scheme.encrypt(x1)
        # tky1 = multi_scheme.keygen(y1)
        # tky2 = multi_scheme.keygen(y2)
        # ctzero = multi_scheme.encrypt(x2)
        #
        # assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1))
        # assert (not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2))
        # assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky1, group_name))




