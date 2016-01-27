# Automaton minimization
Little script for automaton minimization on Python.
To run this script you need to download and install graphviz:
http://www.graphviz.org/
This set of tools allow you to visualize your graph or, just as here, automaton interpreted as graph. As result of script you will have dot-file with structure of graph and two images of initial and minimized automata.

Structure of input data:
size of alphabet
amount of states
number(-s) of initial state(-s)
number(-s) of final states
number symbol number

Last row interpret transition from number to number by symbol and could be repeated many times.

Beware! There is no possibility to work with any alphabet and set of states right now. It will be corrected soon enough.
Also, right now it works on Linux but doesn't work on Windows.
