# An Implementation of Proximity Searchable Encryption (PSE) #

This is an implementation of proximity searchable encryption scheme for the iris biometric
described in https://eprint.iacr.org/2020/1174.

This implementation is a research prototype built for micro-benchmarking 
purposes, and is not intended to be used in production-level code as it has not 
been carefully analyzed for potential security flaws.

Authors:
 * Sohaib Ahmad, University of Connecticut
 * Chloe Cachet, University of Connecticut
 * Luke Demarest, University of Connecticut
 * Benjamin Fuller, University of Connecticut
 * Ariel Hamlin, Northeastern University

Contact Chloe at chloe.cachet@uconn.edu for additional information or questions about the implementation.

## Prerequisites ##

This construction uses the Notre-Dame and IITD datasets. You can find them on the following links:
 * [Notre-Dame](https://cvrl.nd.edu/projects/data/#nd-iris-0405-data-set)
 * [IITD](https://www4.comp.polyu.edu.hk/~csajaykr/IITD/Database_Iris.htm)

Once downloaded, add them to the features folder.


Make sure you have the following installed:
 * [Python 3.x.x](https://www.python.org/downloads/release/python-350/)
 * Make 
 * GCC

Several C and Python libraries are required to build the project, you can either install them one by one or use the script:

    sudo ./install_libraries.sh


## Installation ##

    git clone --recursive https://github.com/chloecachet/pse.git
    cd pse
    ./init_project.sh
	
## Running a Test ##

	python3 tests/test_ipe.py

### Submodules ###

We rely on the following three submodules:
 * [FHIPE](https://github.com/kevinlewi/fhipe) for the matrices generation.
 * [FLINT](http://flintlib.org/) for the C backend. 
 * [Charm](http://charm-crypto.com/) for the pairings implementation. 


