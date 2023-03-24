import pickle


def addconfig(fault, data):
    if fault.startswith('fault2+fault5'):
        return fault2_fault5(data)
    elif fault.startswith('fault2+lockwait'):
        return fault2_lockwait(data)
    elif fault.startswith('fault2+multiindex'):
        return fault2_multiindex(data)
    elif fault.startswith('fault3+IO'):
        return fault3_IO(data)
    elif fault.startswith('fault4+multiindex'):
        return fault4_multiindex(data)
    elif fault.startswith('multiindex+fault3'):
        return multiindex_fault3(data)
    elif fault.startswith('multiindex+IO'):
        return multiindex_IO(data)
    elif fault.startswith('multiindex+lockwait'):
        return multiindex_lockwait(data)
    elif fault.startswith('setknob+fault1'):
        return setknob_fault1(data)


def fault2_fault5(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 20]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [50]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [4000000]:
                c3 = c2 + '/nrows:' + str(nrows)
                # fault5
                d0 = ''
                for ncolumns2 in [5, 10]:
                    d1 = d0 + '/ncolumns:' + str(ncolumns2)
                    for colsize2 in [20]:
                        d2 = d1 + '/colsize:' + str(colsize2)
                        # fault2
                        for bench in ['tpcc', 'tatp', 'smallbank', 'voter']:
                            c4 = c3 + '/bench:' + bench
                            d3 = d2 + '/bench:' + bench
                            for nclient in [5, 10]:
                                c5 = c4 + '/nclient:' + str(nclient)
                                for expid in [1]:
                                    c6 = c5 + '/expid:' + str(expid)
                                    # fault5
                                    for nclient2 in [50, 100, 150]:
                                        d4 = d3 + '/nclient:' + str(nclient2)
                                        for expid2 in [1, 2]:
                                            d5 = d4 + '/expid:' + str(expid2)
                                            data[k].append(c6+d5)
                                            k += 1
    return data


def fault2_lockwait(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 20]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [50]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [4000000]:
                c3 = c2 + '/nrows:' + str(nrows)
                # bench missing
                c4 = ''
                for nclient in [5, 10]:
                    c5 = c4 + '/nclient:' + str(nclient)
                    for expid in [1, 2]:
                        c6 = c5 + '/expid:' + str(expid)
                        # lockwait
                        for bench in ['tpcc', 'tatp', 'smallbank']:
                            c7 = c3 + '/bench:' + bench + c6 + '/bench:' + bench
                            for expid2 in [1, 2]:
                                c8 = c7 + '/expid:' + str(expid2)
                                data[k].append(c8)
                                k += 1
    return data


def fault2_multiindex(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 20]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [50]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [4000000]:
                c3 = c2 + '/nrows:' + str(nrows)
                # multiindex
                d0 = ''
                for ncolumns2 in [50, 80]:
                    d1 = d0 + '/ncolumns:' + str(ncolumns2)
                    for colsize2 in [20]:
                        d2 = d1 + '/colsize:' + str(colsize2)
                        for nrows2 in [400000]:
                            d3 = d2 + '/nrows:' + str(nrows2)
                            # fault2
                            for bench in ['tpcc', 'tatp', 'smallbank', 'voter']:
                                c4 = c3 + '/bench:' + bench
                                d4 = d3 + '/bench:' + bench
                                for nclient in [5, 10]:
                                    c5 = c4 + '/nclient:' + str(nclient)
                                    for expid in [1]:
                                        c6 = c5 + '/expid:' + str(expid)
                                        # multiindex
                                        for nindex10 in [6, 8]:
                                            d5 = d4 + '/nindex10:' + \
                                                str(nindex10)
                                            for nclient2 in [5, 10]:
                                                d6 = d5 + '/nclient:' + \
                                                    str(nclient2)
                                                for expid2 in [1]:
                                                    d7 = d6 + '/expid:' + \
                                                        str(expid2)
                                                    data[k].append(c6+d7)
                                                    k += 1
    return data


def fault3_IO(data):
    k = 0
    c0 = ''
    propcnt = (1, 1, 1, 1)
    cnt = 0
    d0 = ''
    for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
        c1 = c0 + '/bench:' + bench
        d1 = d0 + '/bench:' + bench
        for nclient in [64, 128]:
            c2 = c1 + '/nclient:' + str(nclient)
            for prop in range(propcnt[cnt]):
                c3 = c2 + '/prop:' + str(prop)
                for expid in [1, 2, 3, 4]:
                    c4 = c3 + '/expid:' + str(expid)
                    for expid2 in range(2):
                        d2 = d1 + '/expid:' + str(expid2+1)
                        data[k].append(c4+d2)
                        k += 1
        cnt += 1
    return data


def fault4_multiindex(data):
    k = 0
    c0 = ''
    for ncolumns in [5, 20]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [50]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [4000000]:
                c3 = c2 + '/nrows:' + str(nrows)
                for droprate in [0.5, 0.8]:
                    c4 = c3 + '/droprate:' + str(droprate)
                    # multiindex
                    d0 = ''
                    for ncolumns2 in [50, 80]:
                        d1 = d0 + '/ncolumns:' + str(ncolumns2)
                        for colsize2 in [20]:
                            d2 = d1 + '/colsize:' + str(colsize2)
                            for nrows2 in [400000]:
                                d3 = d2 + '/nrows:' + str(nrows2)
                                # fault4
                                for bench in ['tpcc', 'tatp', 'smallbank', 'voter']:
                                    c5 = c4 + '/bench:' + bench
                                    d4 = d3 + '/bench:' + bench
                                    for nclient in [10]:
                                        c6 = c5 + '/nclient:' + str(nclient)
                                        for expid in [1]:
                                            c7 = c6 + '/expid:' + str(expid)
                                            # multiindex
                                            for nindex10 in [6, 8]:
                                                d5 = d4 + '/nindex10:' + \
                                                    str(nindex10)
                                                for nclient2 in [5, 10]:
                                                    d6 = d5 + '/nclient:' + \
                                                        str(nclient2)
                                                    for expid2 in [1]:
                                                        d7 = d6 + '/expid:' + \
                                                            str(expid2)
                                                        data[k].append(c7+d7)
                                                        k += 1
    return data


def multiindex_fault3(data):
    k = 0
    c0 = ''
    propcnt = (1, 1, 1, 1)
    for ncolumns in [50, 80]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [20]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [400000]:
                c3 = c2 + '/nrows:' + str(nrows)
                # bench missing
                c4 = ''
                for nindex10 in [6, 8]:
                    c5 = c4 + '/nindex10:' + str(nindex10)
                    for nclient in [5, 10]:
                        c6 = c5 + '/nclient:' + str(nclient)
                        for expid in [1]:
                            c7 = c6 + '/expid:' + str(expid)
                            # fault3
                            d0 = ''
                            cnt = 0
                            for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
                                c8 = c3 + '/bench:' + bench + c7
                                d1 = d0 + '/bench:' + bench
                                for nclient in [64, 128]:
                                    d2 = d1 + '/nclient:' + str(nclient)
                                    for prop in range(propcnt[cnt]):
                                        d3 = d2 + '/prop:' + str(prop)
                                        for expid2 in [1, 2]:
                                            d4 = d3 + '/expid:' + str(expid2)
                                            data[k].append(c8+d4)
                                            k += 1
                                cnt += 1
    return data


def multiindex_IO(data):
    k = 0
    c0 = ''
    for ncolumns in [50, 80]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [20]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [400000]:
                c3 = c2 + '/nrows:' + str(nrows)
                d0 = ''
                for bench in ['tpcc', 'tatp', 'smallbank', 'voter']:
                    c4 = c3 + '/bench:' + bench
                    d1 = d0 + '/bench:' + bench
                    for nindex10 in [6, 8]:
                        c5 = c4 + '/nindex10:' + str(nindex10)
                        for nclient in [5, 10]:
                            c6 = c5 + '/nclient:' + str(nclient)
                            for expid in [1]:
                                c7 = c6 + '/expid:' + str(expid)
                                for expid2 in range(2):
                                    d2 = d1 + '/expid:' + str(expid2+1)
                                    data[k].append(c7+d2)
                                    k += 1
    return data


def multiindex_lockwait(data):
    k = 0
    c0 = ''
    for ncolumns in [50, 80]:
        c1 = c0 + '/ncolumns:' + str(ncolumns)
        for colsize in [20]:
            c2 = c1 + '/colsize:' + str(colsize)
            for nrows in [400000]:
                c3 = c2 + '/nrows:' + str(nrows)
                # bench missing
                c4 = ''
                for nindex10 in [6, 8]:
                    c5 = c4 + '/nindex10:' + str(nindex10)
                    for nclient in [5, 10]:
                        c6 = c5 + '/nclient:' + str(nclient)
                        for expid in [1]:
                            c7 = c6 + '/expid:' + str(expid)
                            # lockwait
                            for bench in ['tpcc', 'tatp', 'smallbank']:
                                c8 = c3 + '/bench:' + bench + c7 + '/bench:' + bench
                                for expid2 in range(2):
                                    c9 = c8 + '/expid:' + str(expid2+1)
                                    data[k].append(c9)
                                    k += 1
    return data


def setknob_fault1(data):
    k = 0
    c0 = ''
    # need to be changed according to the environment
    # for shared_buffers in ['256MB', '64MB', '16MB', '4MB']:
    for shared_buffers in ['512MB', '128MB', '32MB', '8MB']:
        c1 = c0 + '/shared_buffers:' + shared_buffers
        # bench missing
        # fault1
        d0 = ''
        for ncolumns2 in [5, 40]:
            d1 = d0 + '/ncolumns:' + str(ncolumns2)
            for colsize2 in [50, 100]:
                d2 = d1 + '/colsize:' + str(colsize2)
                for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
                    c2 = c1 + '/bench:' + bench
                    d3 = d2 + '/bench:' + bench
                    for nclient2 in [100, 150]:
                        d4 = d3 + '/nclient:' + str(nclient2)
                        for expid2 in [1]:
                            d5 = d4 + '/expid:' + str(expid2)
                            data[k].append(c2+d5)
                            k += 1
    return data


folder_list = ['64_256/compound/']
fault_list = ['fault2+fault5', 'fault2+lockwait', 'fault2+multiindex', 'fault3+IO',
              'fault4+multiindex', 'multiindex+fault3', 'multiindex+IO', 'multiindex+lockwait', 'setknob+fault1']
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
