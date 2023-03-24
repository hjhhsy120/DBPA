import sys

f = open('./propconfig/'+sys.argv[4]+'.txt')
cnt = int(sys.argv[5])
prop = ''
for l in f.readlines():
    if cnt == 0:
        prop = l.strip()
    cnt-=1
f.close()
if len(sys.argv) == 7:
    duration = sys.argv[6]
else:
    duration = '60'
f = open(sys.argv[1], 'r')
ot = open(sys.argv[2], 'w')
for l in f.readlines():
    if 'terminals' in l:
        pos1 = l.find('>')
        pos2 = l.find('</')
        l2 = l[:pos1+1] + sys.argv[3] + l[pos2:]
        ot.writelines([l2])
    elif 'weights' in l:
        pos1 = l.find('>')
        pos2 = l.find('</')
        l2 = l[:pos1+1] + prop + l[pos2:]
        ot.writelines([l2])
    elif 'time' in l:
        pos1 = l.find('>')
        pos2 = l.find('</')
        l2 = l[:pos1+1] + duration + l[pos2:]
        ot.writelines([l2])
    else:
        ot.writelines([l])

ot.close()
f.close()
print('set config')