from Client import *
import time
import h5py
import sys

def main():

    # The number of neighbors to use for classification.
    k = 10

    ###########################################################################
    #  Load the dataset
    ###########################################################################
    print("\n=========================")
    print("Precision: uint8")
    print("Distance:  L1")
    print("=========================")

    print("\nLoading dataset...")
    sys.stdout.flush()

    # Load the labels for the training and test vectors.
    # Note: the slice operator at the end tells h5py how much of the matrix to load
    # into memory, so [:] loads the whole thing.
    y_train = h5py.File('./data/y_train.h5', 'r')['y_train'][:]
    y_test = h5py.File('./data/y_test.h5', 'r')['y_test'][:]
    X_test = h5py.File('./data/X_test_uint8.h5', 'r')['X_test'][:]

    print("  Test set     [%5d x %d]" % (len(X_test), len(X_test[0])))
    sys.stdout.flush()

    ###########################################################################
    #  Setup Nearist hardware
    ###########################################################################

    print("\nOpening connection to appliance...")
    sys.stdout.flush()
    
    c = Client()
    
    # Establish a connection to the appliance.  
    # NOTE - These values should be updated with the ones you received.
    c.open(host='000.000.000.000', port=0, api_key='')

    c.reset()

    c.set_distance_mode(DistanceMode.L1)
    c.set_query_mode(QueryMode.KNN_A)
    c.set_read_count(k)

    ###########################################################################
    #  Load the dataset (the training vectors) into Nearist DRAM
    ###########################################################################

    print("\nLoading dataset vectors from appliance harddisk...")
    sys.stdout.flush()
    
    # Load the training vectors *remotely* from the appliance harddisk.
    c.load_dataset_file(file_name='/nearist/MNIST/X_train_uint8.h5',
                        dataset_name='X_train')

    print("    Loaded.")
    sys.stdout.flush()

    ###########################################################################
    #  Run classification experiment
    ###########################################################################

    # Time this step.
    t0 = time.time()

    print("\nRunning %d-NN Classification..." % k)
    sys.stdout.flush()

    # Perform the queries.    
    result_batch = c.query(X_test.tolist())

    numRight = 0

    # For each of the query vectors...
    for query_results in result_batch:

        # Reset class tallies
        arrNumClass = [0] * 10

        # For each of the 'k' results of the query...
        for result in query_results:

            # Get the index of the matching dataset vector.
            ds_id = result['ds_id']

            # Tally the class.
            arrNumClass[y_train[ds_id]] += 1

        # Choose the winning class by checking which had the most "votes".
        p = arrNumClass.index(max(arrNumClass))

        # Check if we predicted the right class.
        if (p == y_test[i]):
            numRight += 1;

    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)
    print("  done in %.3fsec" % elapsed)

    print( '%d of %d correct (%.2f%%)' % (numRight, len(y_test), float(numRight) / len(y_test) * 100.0))

    c.close()


if __name__ == "__main__":
    main()
