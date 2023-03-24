import pickle


def addconfig(fault, data):
    if fault.startswith('fault1'):
        return fault1(data)
    elif fault.startswith('fault24'):
        return fault24(data)
    elif fault.startswith('fault3'):
        return fault3(data)
    elif fault.startswith('fault5'):
        return fault5(data)
    elif fault.startswith('multiindex'):
        return multiindex(data)
    elif fault.startswith('stress'):
        return IO(data)
    elif fault.startswith('lockwait'):
        return lockwait(data)
    elif fault.startswith('setknob'):
        return setknob(data)


def fault1(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 10, 15, 20, 25, 30, 35, 40]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [50, 100]:
            c2 = c1 + '/colsize:' + str(colsize)
            for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
                c3 = c2 + '/bench:' + bench
                for nclient in [50, 100, 150]:
                    c4 = c3 + '/nclient:' + str(nclient)
                    for expid in [1, 2, 3]:
                        c5 = c4 + '/expid:' + str(expid)
                        data[k].append(c5)
                        k += 1
    return data


def fault24(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 10, 20]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [50, 100]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [2000000, 4000000]:
                c3 = c2 + '/nrows:' + str(nrows)
                for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
                    c4 = c3 + '/bench:' + bench
                    for nclient in [5, 10]:
                        c5 = c4 + '/nclient:' + str(nclient)
                        for expid in [1, 2, 3]:
                            c6 = c5 + '/expid:' + str(expid)
                            data[k].append(c6)
                            k += 1
                for droprate in [0.5, 0.8]:
                    c4 = c3 + '/droprate:' + str(droprate)
                    for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
                        c5 = c4 + '/bench:' + bench
                        for nclient in [5, 10]:
                            c6 = c5 + '/nclient:' + str(nclient)
                            for expid in [1, 2, 3]:
                                c7 = c6 + '/expid:' + str(expid)
                                data[k].append(c7)
                                k += 1
    return data


def fault3(data):
    k = 0
    c0 = ''
    propcnt = (7, 4, 1, 6)
    cnt = 0
    for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
        c1 = c0 + '/bench:' + bench
        for nclient in [64, 128]:
            c2 = c1 + '/nclient:' + str(nclient)
            for prop in range(propcnt[cnt]):
                c3 = c2 + '/prop:' + str(prop)
                for expid in [1, 2, 3, 4, 5]:
                    c4 = c3 + '/expid:' + str(expid)
                    data[k].append(c4)
                    k += 1
        cnt += 1
    return data


def fault5(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 10, 15, 20]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [20, 40, 60, 80]:
            c2 = c1 + '/colsize:' + str(colsize)
            for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
                c3 = c2 + '/bench:' + bench
                for nclient in [50, 100, 150]:
                    c4 = c3 + '/nclient:' + str(nclient)
                    for expid in [1, 2, 3]:
                        c5 = c4 + '/expid:' + str(expid)
                        data[k].append(c5)
                        k += 1
    return data


def multiindex(data):
    k = 0
    c0 = ''
    for ncolumns in [50, 60, 70, 80]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [10, 20]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [200000, 400000]:
                c3 = c2 + '/nrows:' + str(nrows)
                for bench in ['tpcc', 'tatp', 'smallbank','voter']:
                    c4 = c3 + '/bench:' + bench
                    for nindex10 in [6, 8]:
                        c5 = c4 + '/nindex10:' + str(nindex10)
                        for nclient in [5, 10]:
                            c6 = c5 + '/nclient:' + str(nclient)
                            for expid in [1, 2, 3]:
                                c7 = c6 + '/expid:' + str(expid)
                                data[k].append(c7)
                                k += 1
    return data


def IO(data):
    k = 0
    c0 = ''
    for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
        c1 = c0 + '/bench:' + bench
        for expid in range(15):
            c2 = c1 + '/expid:' + str(expid+1)
            data[k].append(c2)
            k += 1
    return data


def lockwait(data):
    k = 0
    c0 = ''
    for bench in ['tpcc', 'tatp', 'smallbank']:
        c1 = c0 + '/bench:' + bench
        for expid in range(10):
            c2 = c1 + '/expid:' + str(expid+1)
            data[k].append(c2)
            k += 1
    return data


def setknob(data):
    k = 0
    c0 = ''
    for shared_buffers in ['256MB', '64MB', '16MB', '4MB']:    ## need to be changed according to the environment
    # for shared_buffers in ['512MB', '128MB', '32MB', '8MB']:    
        c1 = c0 + '/shared_buffers:' + shared_buffers
        for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
            c2 = c1 + '/bench:' + bench
            data[k].append(c2)
            k += 1
    return data


folder_list = ['64_128/single/']
fault_list = ['fault1', 'fault24', 'fault3_all', 'fault5',
              'multiindex', 'stress_all', 'lockwait', 'setknob']
for folder in folder_list:
    for fault in fault_list:
        fname = folder + fault + '_data.pickle'
        try:
            f = open(fname, 'rb')
            data = pickle.load(f)
            f.close()
        except:
            print(fname, 'not found')
            continue
        data_with_config = addconfig(fault, data)
        f = open(folder[:-1] + '_with_config/' + fault + '_data.pickle', 'wb')
        pickle.dump(data_with_config, f)
        f.close()
