import inspect
import os
import sys
import subprocess

# "enum" analogue for list
# Q - states, А - alphabet, Т - transitions, S - initial states, F - final (accept) states
Q = 0
A = 1
T = 2
S = 3
F = 4

# Reading from file
def fa_read(filename):
    fa = [None] * 5
    f = open(filename, 'r')
    alphabet = int(str(f.readline()).rstrip('\n'))
    fa[A] = [chr(97 + a) for a in range(0, alphabet)]
    state = int(str(f.readline()).rstrip('\n'))
    fa[Q] = [s for s in range(0, state)]
    s0 = int(str(f.readline()).rstrip('\n'))
    fa[S] = [s0]
    accept = str(f.readline()).rstrip('\n').split(' ')
    fa[F] = [int(accept[ac]) for ac in range(1, len(accept))]
    fa[T] = [[[] for i in range(0, len(fa[A]))] for j in range(0, len(fa[Q]))]
    transall = f.readlines()
    for trans in range(0, len(transall)):
        t = str(transall[trans]).rstrip('\n').split(' ')
        fa[T][int(t[0])][ord(t[1])-97].append(int(t[2]))
    return fa

# Automaton's image generation
def fa_gv(fa, filename, pngname):
    # DOT-file generation for package of open-source tools graphviz
    f = open(filename, 'w')
    f.write('digraph fa {\n')
    # Description of initial states
    f.write('{\n')
    f.write('node [shape=circle style=filled]\n')
    f.write('[fillcolor=greenyellow] ')
    for s in fa[S]:
        f.write(str(s) + ' ')
    f.write('\n}\n')
    # Building automaton from left to right
    f.write('rankdir=LR;\n')
    # Final states placed in double circle
    f.write('node[shape=doublecircle];')
    for i in fa[F]:
        f.write(str(fa[Q][i]) + ';')
    f.write('\nnode[shape=circle];\n')
    for t1 in range(0, len(fa[Q])):
        for a in range(0, len(fa[A])):
            for t2 in fa[T][t1][a]:
                f.write(str(fa[Q][t1]) + '->' + str(fa[Q][t2]))
                f.write('[label=' + str(fa[A][a]) + '];\n')
    f.write('}\n')
    f.close()
    # Location of current directory of this program
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    dotfile, dotapp, resname = "", "", ""

    # Location of graphviz installation directory on Windows and Linux (MacOS X too, possibly)
    if sys.platform == "win32":
        import winreg
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        # See 'alternate registry view'
        winAccessKey = winreg.KEY_WOW64_64KEY | winreg.KEY_READ
        aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Folders", 0, winAccessKey)
        # Unreliable way to receive graphviz 'bin'-directory since graphviz has bad records in registry
        i = 0
        while True:
            try:
                name, value, type = winreg.EnumValue(aKey, i)
                if "Graphviz" in name and "bin" in name:
                    dotdir = name
                    break
                i += 1
            except WindowsError:
                print("It end's here")
                break
        del winreg
        resname = currentdir + '\\' + pngname + '.png'
        dotapp = dotdir + 'dot'
        dotfile = currentdir + '\\' + filename
        opener = [resname]
    else:
        resname = currentdir + '/' + pngname + '.png'
        dotapp = "dot"
        dotfile = currentdir + '/' + filename
        if sys.platform == "darwin":
            opener = ["open", resname]
        else:
            opener = ["xdg-open", resname]

    # Image generation via terminal by dot-tool from generated before *.dot-file into *.png-format
    subprocess.call([dotapp, dotfile, "-Tpng", "-o", resname])
    # Open image
    subprocess.call([resname], shell = True)


# Automaton reverse
def fa_rev(fa):
    rfa = [list(fa[Q]), list(fa[A]), [], list(fa[F]), list(fa[S])]
    rfa[T] = [[[] for i in range(0, len(fa[A]))] for j in range(0, len(fa[Q]))]
    for t1 in range(0, len(fa[Q])):
        for a in range(0, len(fa[A])):
            for t2 in fa[T][t1][a]:
                rfa[T][t2][a].append(t1)
    return rfa


# Automaton determinization
# For the detailed information see any book, for example
# "Introduction to Automata Theory, Languages, and Computation"
# by J.E. Hopcroft, R. Motwani and J.D. Ullman
def fa_det(fa):
	# Set of sets q contains set of initial states
	# reachable function finds reachable states from l-th set of initial states
	# thus we have procedure similar to queue but with ability to modify "queue"
	# Accessible states for l-th set of initial states from set q (reorganization of queue)
    def reachable(q, l):
        t = []
        for a in range(0, len(fa[A])):
            ts = set()
            for i in q[l]:
            	# Union of reachable via symbol a states
                ts |= set(fa[T][i][a])
            # If none of states is reachable then add empty list and proceed to next symbol
            if not ts:
                t.append([])
                continue
            # Check if created set t already exists in "queue" q
            try:
                i = q.index(ts)
            # If it does not exist then append this set to queue and rename with new last index
            except ValueError:
                i = len(q)
                q.append(ts)
            t.append([i])
        # As result we have extended queue and transition list by symbols to new element
        return t

    dfa = [[], list(fa[A]), [], [0], []]
    q = [set(fa[S])]
    while len(dfa[T]) < len(q):
        dfa[T].append(reachable(q, len(dfa[T])))
    dfa[Q] = range(0, len(q))
    dfa[F] = [q.index(i) for i in q if set(fa[F]) & i]
    return dfa


# Brzozowski's minimization algorithm
def fa_min(fa):
    return fa_det(fa_rev(fa_det(fa_rev(fa))))


fa = fa_read('sample.txt')

fa_gv(fa, 'fa_min.dot', 'InitialAutomaton')
fa_gv(fa_min(fa), 'fa_min.dot', 'MinimizedAutomaton')