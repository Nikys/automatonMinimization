import inspect, os, sys, subprocess

# "enum" для списку
# Q - стани, А - алфавіт, Т - переходи, S - початкові стани, F - кінцеві стани
Q = 0
A = 1
T = 2
S = 3
F = 4

# Зчитування з файлу
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

# Генерація зображення автомату
def fa_gv(fa, filename, pngname):
    # Генерація DOT-коду для вільної утиліти graphviz
    f = open(filename, 'w')
    f.write('digraph fa {\n')
    # Опис початкових станів
    f.write('{\n')
    f.write('node [shape=circle style=filled]\n')
    f.write('[fillcolor=greenyellow] ')
    for s in fa[S]:
        f.write(str(s) + ' ')
    f.write('\n}\n')
    # Побудова автомату зліва направо
    f.write('rankdir=LR;\n')
    # Кінцеві стани у подвійному колі
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
    # Поточна директорія в якій розташована програма
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    # Директорія, в якій розташована програма і dot-файл
    dotdirlinux = '/usr/bin'

    # Генерація зображення у командному рядку з відповідного згенерованого DOT-файлу
    os.system('"' + dotdir + '/dot" ' + currentdir + '/' + filename + \
              ' -Tpng -o ' + currentdir + '/' + pngname + '.png')
    # Запуск зображення
    resname = currentdir + '/' + pngname + '.png'
    if sys.platform == "win32":
        os.startfile(resname)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, resname])


# Обернення автомату
def fa_rev(fa):
    rfa = [list(fa[Q]), list(fa[A]), [], list(fa[F]), list(fa[S])]
    rfa[T] = [[[] for i in range(0, len(fa[A]))] for j in range(0, len(fa[Q]))]
    for t1 in range(0, len(fa[Q])):
        for a in range(0, len(fa[A])):
            for t2 in fa[T][t1][a]:
                rfa[T][t2][a].append(t1)
    return rfa


# Детермінізація автомату
def fa_det(fa):
    # Досяжні з l-ї множини списку множин початкових станів q (процедурна реорганізація "черги")
    def reachable(q, l):
        t = []
        for a in range(0, len(fa[A])):
            ts = set()
            for i in q[l]:
                # Об'єднання досяжних за символом a станів автомату (з відповідної множини початкових станів)
                ts |= set(fa[T][i][a])
            # Якщо жоден стан не досягається, то додаємо порожній список і переходимо до наступного символу
            if not ts:
                t.append([])
                continue
            # Перевірка, чи наявна отримана вище об'єднана множина станів у списку q
            try:
                i = q.index(ts)
            # Якщо не наявна, то позначаємо індекс на останню позицію, додаємо множину
            except ValueError:
                i = len(q)
                q.append(ts)
            t.append([i])
        # На виході отримаємо збільшену (можливо) чергу і список переходів за символами для нового елементу
        # До того ж, в ході процедури нові множини ітеративно перейменовуються, але доступ існує через q
        return t

    dfa = [[], list(fa[A]), [], [0], []]
    q = [set(fa[S])]
    while len(dfa[T]) < len(q):
        dfa[T].append(reachable(q, len(dfa[T])))
    dfa[Q] = range(0, len(q))
    dfa[F] = [q.index(i) for i in q if set(fa[F]) & i]
    return dfa


# Алгоритм Бржозовського
def fa_min(fa):
    return fa_det(fa_rev(fa_det(fa_rev(fa))))


fa = fa_read('sample.txt')

fa_gv(fa, 'fa_min.dot', 'StartAutomaton')
fa_gv(fa_min(fa), 'fa_min.dot', 'MinimizedAutomaton')