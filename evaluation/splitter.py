
import pickle
import math
def load_file(fname):
    f = open(fname, 'rb')
    data = pickle.load(f)
    f.close()
    return data

def load_seq(fname):
    result = []
    f = open(fname, 'r',encoding='utf-8')
    for l in f.readlines():
        ll = l.strip()
        if 'benchmark ' in ll and ll.endswith('start'):
            result.append(ll[ll.find('benchmark ')+len('benchmark ') : ll.find('start')-1])
    return result


def split_data(hard, data_name):
    data = load_file(hard + '/' + data_name + '_data.pickle')
    seq = load_seq(hard + '/' + data_name + '.txt')
    envs = set(seq)
    datasets = {}
    for env in envs:
        datasets[env] = []
    tot = len(data)
    batch = math.ceil(tot / len(seq))
    if data_name == 'fault3':
        datasets['tpcc'] += data[0 : 70]
        datasets['tatp'] += data[70 : 110]
        datasets['voter'] += data[110 : 120]
        datasets['smallbank'] += data[120 :]
        for env in envs:
            f = open(hard + '/' + env + '/' + data_name + '_data.pickle', 'wb')
            pickle.dump(datasets[env], f)
            f.close()
        print(data_name, tot, len(datasets['tpcc']), len(datasets['tatp']),len(datasets['voter']),len(datasets['smallbank']))
    else:    
        for i in range(len(seq)):
            datasets[seq[i]] += data[i*batch : (i+1)*batch]
        for env in envs:
            f = open(hard + '/' + env + '/' + data_name + '_data.pickle', 'wb')
            pickle.dump(datasets[env], f)
            f.close()
        print(data_name, tot, len(seq), batch)

if __name__=='__main__':
    fault_list = ['setknob', 'multiindex', 'lockwait', 'fault1', 'fault2', 'fault3', 'fault4', 'fault5', 'stress']
    for data_name in fault_list:
        split_data('./data/32_128/single', data_name)
        split_data('./data/32_256/single', data_name)
        split_data('./data/64_128/single', data_name)
        split_data('./data/64_256/single', data_name)
