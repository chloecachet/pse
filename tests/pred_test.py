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

import sys, os, math, argparse, time
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

from pse import predipe, prox_search, multibasispredipe

if __name__ == "__main__":

    st = time.time()

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

    #group_name = 'SS512'
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

    et = time.time()
    print("Finished set-up in " + str(et-st) + " seconds")

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

        print("Testing multi basis scheme with 1 base")

        x1 = [1, -1, -1, 1]
        x2 = [0, 0, 0, 0]
        y1 = [1, 1, 1, 1]
        y2 = [1, 5, 1, -3]

        multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=1)
        multi_scheme.generate_keys()
        ctx = multi_scheme.encrypt(x1)
        tky1 = multi_scheme.keygen(y1)
        tky2 = multi_scheme.keygen(y2)
        ctzero = multi_scheme.encrypt(x2)
        
        assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1))
        assert (not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2))
        assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky1, group_name))

        print("Testing multi basis scheme with 2 bases")

        multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=2)
        multi_scheme.generate_keys()
        ctx = multi_scheme.encrypt(x1)
        tky1 = multi_scheme.keygen(y1)
        tky2 = multi_scheme.keygen(y2)
        ctzero = multi_scheme.encrypt(x2)
        
        assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1))
        assert (not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2))
        assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky1, group_name))

        print("Testing multi basis scheme with 4 bases")

        multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=4)
        multi_scheme.generate_keys()
        ctx = multi_scheme.encrypt(x1)
        tky1 = multi_scheme.keygen(y1)
        tky2 = multi_scheme.keygen(y2)
        ctzero = multi_scheme.encrypt(x2)
        
        start_time_1 = time.time()
        assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1))
        end_time_1 = time.time()
        start_time_2 = time.time()
        assert (not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2))
        end_time_2 = time.time()
        start_time_3 = time.time()
        assert (multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky1, group_name))
        end_time_3 = time.time()

        print("Total elapsed time for first decrypt: " + str(end_time_1-start_time_1))
        print("Total elapsed time for second decrypt: " + str(end_time_2-start_time_2))
        print("Total elapsed time for third decrypt: " + str(end_time_3-start_time_3))

    elif vector_length > 4:
        
        print("Timings for vector_length = " + str(vector_length))

        x1 = []
        x2 = []
        y1 = []
        y2 = []

        for i in range(vector_length):
            x2.append(0)
            x1.append(i % 2)
            y1.append(i % 8)
            y2.append(i % 5)

        # number of bases
        nb = math.ceil(vector_length/40)

        multi_scheme = multibasispredipe.MultiBasesPredScheme(n=vector_length, group_name=group_name, num_bases=nb, simulated = True)
        multi_scheme.generate_keys()

        # arrays for timings
        KGTimes = []
        EncTimes = []
        DecTimes = []

        # iterations
        n = 100

        print("Timing key gen...")
        for i in range(n):
            kg_start_1 = time.time()
            tky1 = multi_scheme.keygen(y1)
            kg_end_1 = time.time()
            kg_start_2 = time.time()
            tky2 = multi_scheme.keygen(y2)
            kg_end_2 = time.time()
            KGTimes.append(((kg_end_1-kg_start_1)+(kg_end_2-kg_start_2))/2)
        
        print("Timing encrypt...")
        for i in range(n):
            enc_start_1 = time.time()
            ctx = multi_scheme.encrypt(x1)
            enc_end_1 = time.time()
            enc_start_2 = time.time()
            ctzero = multi_scheme.encrypt(x2)
            enc_end_2 = time.time()
            EncTimes.append(((enc_end_1-enc_start_1)+(enc_end_2-enc_start_2))/2)
        
        print("Timing decrypt...")
        for i in range(n):
            dec_start_1 = time.time()
            res1 = multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctzero, tky1)
            dec_end_1 = time.time()
            dec_start_2 = time.time()
            res2 = not multi_scheme.decrypt(multi_scheme.getPublicParameters(), ctx, tky2)
            dec_end_2 = time.time()
            DecTimes.append(((dec_end_1-dec_start_1)+(dec_end_2-dec_start_2))/2)

        DecSum = 0
        KGSum = 0 
        EncSum = 0

        for t in KGTimes:
            KGSum += t

        for t in EncTimes:
            EncSum += t

        for t in DecTimes:
            DecSum += t
        
        print("Average time for keyGen: " + str(KGSum/n))
        print("Average time for encrypt: " + str(EncSum/n))
        print("Average time for decrypt: " + str(DecSum/n))

        # find variance and standard deviation
        KGVar = 0
        EncVar = 0
        DecVar = 0

        for t in KGTimes:
            KGVar = (t-(KGSum/n))**2
            KGVar = KGVar/(n-1)

        for t in EncTimes:
            EncVar = (t-(EncSum/n))**2
            EncVar = EncVar/(n-1)

        for t in DecTimes:
            DecVar = (t-(DecSum/n))**2
            DecVar = DecVar/(n-1)

        print("KeyGen variance is " + str(KGVar))
        print("Enc variance is " + str(EncVar))
        print("Dec variance is " + str(DecVar))

        '''
        print("Testing Proximity Search")

        prox_start = time.time()

        data = [x1, x2]
        database.encrypt_dataset(data)
        print("Size of DB "+str(database.get_database_size()))
        print("Size of Secret Key "+str(database.get_seckey_size()))
        query = y1
        encrypted_query = database.generate_query(query, 1)
        #assert(len(encrypted_query)==2)
        relevant_indices = database.search(encrypted_query)
        #assert(len(relevant_indices)==1 and relevant_indices[0] == 0)
        encrypted_query = database.generate_query(query, 0)
        #assert (len(encrypted_query) == 1)
        relevant_indices = database.search(encrypted_query)
        #assert (len(relevant_indices) == 0)

        prox_end = time.time()

        print("Total time for prox search: " + str(prox_end-prox_start))
        '''





