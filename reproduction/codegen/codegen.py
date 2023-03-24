
import argparse
from asyncore import loop
import os
import xml.dom.minidom

# parse cmd args
def parse_args():
    parser = argparse.ArgumentParser(description='DBPA Codegen')
    parser.add_argument('--config', type=str, default='template.xml', help='XML configurations')
    parser.add_argument('--output', type=str, default='temp', help='output folder')
    parser.add_argument("--nodool", action='store_true', help='not use dool')
    args = parser.parse_args()
    try:
        DOMTree = xml.dom.minidom.parse(args.config)
        config = DOMTree.documentElement
    except Exception as e:
        print(e)
        print('ERROR in XML config file. Abort.')
        exit()
    try:
        if not os.path.exists(args.output):
            os.mkdir(args.output)
    except Exception as e:
        print(e)
        print('ERROR in output path. Abort.')
        exit()
    return config, args.output, args.nodool

def getinfo(config, name, notnull=False):
    try:
        info = config.getElementsByTagName(name)[0].childNodes[0].data
        return info.strip()
    except:
        if notnull:
            print('Missing ' + config.nodeName + ' ' + name +'. Abort.')
            exit()
        else:
            return None

def getattr(config, name, notnull=False):
    try:
        info = config.getAttribute(name)
        return info
    except:
        if notnull:
            print('Missing attribute '+name +'. Abort.')
            exit()
        else:
            return None

def sh_cmd(cmd, f, ntabs):
    f.writelines([' '*(4*ntabs), cmd, '\n'])

def sh_for(name, vals, f, ntabs):
    if vals is None:
        return 0
    cmd = 'for {} in {}; do'.format(name, ' '.join(vals.strip().split(',')))
    sh_cmd(cmd, f, ntabs)
    return 1


def sh_workload(workload, f, ntabs):
    bench = getinfo(workload, 'bench', True)
    xml_star = getinfo(workload, 'xml', True)
    sh_for('bench', bench, f, ntabs)
    sh_cmd('echo -e "benchmark ${bench} start $(date +%Y-%m-%d\\ %H:%M:%S)"', f, ntabs+1)
    cmd = '$OLTPBENCH_HOME/oltpbenchmark -b $bench -c ' + xml_star.replace('*', '${bench}') + ' --execute=true -s 15 -o outputfile &'
    sh_cmd(cmd, f, ntabs+1)
    sleep_time = getinfo(workload, 'sleep')
    if not sleep_time is None:
        sh_cmd('sleep ' + sleep_time, f, ntabs+1)
    

def sh_endworkload(f, ntabs):
    sh_cmd('ps -ef | grep oltpbench | awk \'$0 !~ /grep/ {print $2}\' | xargs kill -9', f, ntabs)
    sh_cmd('sleep 3', f, ntabs)
    sh_cmd('rm -r -f results', f, ntabs)
    sh_cmd('echo -e "benchmark ${bench} end"', f, ntabs)
    sh_cmd('done', f, ntabs-1)

def sh_env(env, f):
    tp = getattr(env, 'type')

    # bad knobs
    if tp == 'knob':
        print('environment: bad knobs')
        env_dict = {}
        for key in ['db', 'knob', 'normal', 'bad']:
            env_dict[key] = getinfo(env, key, True)
        
        cmd = 'normal_values=(' + env_dict['normal'] + ')'
        sh_cmd(cmd, f, 0)
        cmd = 'bad_values=(' + ' '.join(env_dict['bad'].split(',')) + ')'
        sh_cmd(cmd, f, 0)
        bad_cnt = len(env_dict['bad'].split(','))
        cmd = 'for ((i = 0; i < ' + str(bad_cnt) + '; i++)); do'
        sh_cmd(cmd, f, 0)
        cmd = 'python set_knob.py -db ' + env_dict['db'] + ' -kn ' + env_dict['knob'] + ' -kv ${bad_values[i]}'
        sh_cmd(cmd, f, 1)

        # for restart
        restart_cmd = getinfo(env, 'restart_cmd')
        if not restart_cmd is None:
            f.writelines([restart_cmd, '\n'])
        else:
            print('no restart')
        return 1

    # shell commands, such as stress-ng for IO saturation
    elif tp == 'cmd':
        print('environment: set by commands')
        cmd = getinfo(env, 'cmd_begin')
        if cmd is None:
            cmd = getinfo(env, 'cmd', True)
        f.writelines([cmd, '\n'])
        ntabs = getinfo(env, 'ntabs')
        try:
            ntabs = int(ntabs)
        except:
            ntabs = 0
            print('no tabs')
        return ntabs

    # others (user-defined)
    else:
        print('environment: user-defined')
        ntabs = getinfo(env, 'ntabs')
        try:
            ntabs = int(ntabs)
        except:
            ntabs = 0
            print('no tabs')
        sh_cmd('# YOUR CODE HERE: ENVIRONMENT SETTINGS', f, 0)
        return ntabs

def sh_endenv(env, f):
    tp = getattr(env, 'type')

    # bad knobs
    if tp == 'knob':
        sh_cmd('done', f, 0)
        env_dict = {}
        for key in ['db', 'knob', 'normal', 'bad']:
            env_dict[key] = getinfo(env, key, True)
        cmd = 'python set_knob.py -db ' + env_dict['db'] + ' -kn ' + env_dict['knob'] + ' -kv ${normal_values[0]}'
        sh_cmd(cmd, f, 0)
        restart_cmd = getinfo(env, 'restart_cmd')
        if not restart_cmd is None:
            f.writelines([restart_cmd, '\n'])
    elif tp == 'cmd':
        cmd = getinfo(env, 'cmd_end')
        if not cmd is None:
            f.writelines([cmd, '\n'])
        
def sh_table(table, f, ntabs):
    cnt = ntabs

    # create table
    print('create table')
    d = {}
    for key in ['ncolumns', 'colsize', 'nrows']:
        d[key] = getinfo(table, key)
        cnt += sh_for(key, d[key], f, cnt)
        
    cmd = 'python createt.py'
    for key in ['ncolumns', 'colsize', 'nrows']:
        if not d[key] is None:
            cmd += ' --{} ${}'.format(key, key)
    sh_cmd(cmd, f, cnt)

    # indexes
    nindex10 = getinfo(table, 'nindex10')
    if not nindex10 is None:
        print('add index')
        cnt += sh_for('nindex10', nindex10, f, cnt)
        sh_cmd('nindex=$(expr $ncolumns \* $nindex10 / 10)', f, cnt)
        sh_cmd('python add_index.py -c 0', f, cnt)
        sh_cmd('python add_index.py -c $nindex', f, cnt)
        sh_cmd('python id_index.py -c 1', f, cnt)

    # droprate for vacuum
    droprate = getinfo(table, 'droprate')
    if not droprate is None:
        print('drop some data')
        # check if nrows is defined
        _ = getinfo(table, 'nrows', True)
        cnt += sh_for('droprate', droprate, f, cnt)
        sh_cmd('python deletet.py --nrows $nrows --droprate $droprate', f, cnt)

    return cnt

def sh_inject(inject, f, ntabs):
    tp = getattr(inject, 'type')

    # python scripts
    if tp == 'queries':
        print('inject: queries')

        # file name
        file = getinfo(inject, 'file', True)

        # loops
        loopss = inject.getElementsByTagName('loops')
        cnt = ntabs
        if len(loopss) > 0:
            loops = loopss[0]
            for node in loops.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    name = node.nodeName
                    val = getinfo(loops, name, True)
                    cnt += sh_for(name, val, f, cnt)

        # expid
        expcnt = getinfo(inject, 'expcnt')
        if not expcnt is None:
            cnt += sh_for('expid', ','.join([str(x+1) for x in range(int(expcnt))]), f, cnt)

        # python params
        cmd = 'python ' + file
        loop_params = getinfo(inject, 'loop_params')
        if not loop_params is None:
            for param in loop_params.split(','):
                cmd += ' --{} ${}'.format(param, param)
        other_paramss = inject.getElementsByTagName('other_params')
        if len(other_paramss) > 0:
            other_params = other_paramss[0]
            for node in other_params.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    name = node.nodeName
                    val = getinfo(other_params, name, True)
                    cmd += ' --' + name + ' ' + val
        sh_cmd(cmd, f, cnt)

        cmd = getinfo(inject, 'cmd')
        if not cmd is None:
            f.writelines([cmd, '\n'])

        # done
        for i in range(cnt-ntabs):
            sh_cmd('done', f, cnt - i - 1)
        
    elif tp == 'cmd':
        print('inject: commands')
        cmd = getinfo(inject, 'cmd', True)
        f.writelines([cmd, '\n'])
    else:
        print('inject: user-defined')
        sh_cmd('# YOUR CODE HERE: ANOMALY INJECTION', f, ntabs)


def gen_single_sh(config, output, nodool):
    name = getinfo(config, 'name', True)
    f = open(os.path.join(output, name+'.sh'), 'w')
    f.writelines(['#!/bin/bash/\n\n'])

    # environment (for db env anomalies)
    envs = config.getElementsByTagName('env')
    if len(envs) > 0:
        ntabs_env = sh_env(envs[0], f)
    else:
        ntabs_env = 0

    # start dool
    if not nodool:
        sh_cmd('bash start_dool_big.sh', f, ntabs_env)

    tables = config.getElementsByTagName('table')
    if len(tables) > 0:
        ntabs_table = sh_table(tables[0], f, ntabs_env)
    else:
        ntabs_table = 0


    workloads = config.getElementsByTagName('workload')
    if len(workloads) > 0:
        sh_workload(workloads[0], f, ntabs_env + ntabs_table)
        ntabs_bench = 1
    else:
        ntabs_bench = 0
        
    injects = config.getElementsByTagName('inject')
    if len(injects) > 0:
        sh_inject(injects[0], f, ntabs_env + ntabs_table + ntabs_bench)

    # done
    if len(workloads) > 0:
        sh_endworkload(f, ntabs_env + ntabs_table + 1)

    for i in range(ntabs_table):
        sh_cmd('done', f, ntabs_env + ntabs_table - 1 - i)

    # end dool
    sleep_time = getinfo(config, 'sleep')
    if not sleep_time is None:
        sh_cmd('sleep ' + sleep_time, f, ntabs_env)
    if not nodool:
        sh_cmd('bash stop_dool_big.sh', f, ntabs_env)

    if len(envs) > 0:
        sh_endenv(envs[0], f)

    f.close()

if __name__ == '__main__':
    config, output, nodool = parse_args()
    gen_single_sh(config, output, nodool)

