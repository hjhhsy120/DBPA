global pg_user
pg_user = os.getenv('DSTAT_PG_USER') or os.getenv('USER')

global pg_pwd
pg_pwd = os.getenv('DSTAT_PG_PWD')

global pg_host
pg_host = os.getenv('DSTAT_PG_HOST')

global pg_port
pg_port = os.getenv('DSTAT_PG_PORT')


class dstat_plugin(dstat):
    """
    Plugin for PostgreSQL connections.
    """

    def __init__(self):
        self.name = 'postgresql all'
        dbsize_nick = ('size', 'grow', 'insert', 'update', 'delete')
        dbsize_vars = ('dbsize', 'grow_rate', 'inserted',
                       'updated', 'deleted')
        trans_nick = ('comm', 'roll')
        trans_vars = ('commit', 'rollback')
        self.nick = ('clean', 'back',
                     'alloc',
                     'heapr', 'heaph', 'ratio'
                     )+dbsize_nick+trans_nick
        self.vars = ('clean', 'backend',
                     'alloc',
                     'heap_blks_read', 'heap_blks_hit', 'ratio_hit',
                     )+dbsize_vars+trans_vars
        self.type = 'f'
        self.width = 5
        self.scale = 1

        self.last_commit = 0
        self.last_rollback = 0

    def check(self):
        global psycopg2
        import psycopg2
        try:
            args = {}
            if pg_user:
                args['user'] = pg_user
            if pg_pwd:
                args['password'] = pg_pwd
            if pg_host:
                args['host'] = pg_host
            if pg_port:
                args['port'] = pg_port

            self.db = psycopg2.connect(**args)
        except Exception as e:
            raise Exception('Cannot interface with PostgreSQL server, %s' % e)

    def extract(self):
        try:
            c = self.db.cursor()
            c.execute(
                "select buffers_clean,buffers_backend,buffers_alloc from pg_stat_bgwriter")
            clean, backend, alloc = c.fetchone()
            c.execute(
                "select sum(heap_blks_read), sum(heap_blks_hit) FROM pg_statio_all_tables")
            heap_blks_read, heap_blks_hit = c.fetchone()
            self.set2['heap_blks_read'] = heap_blks_read
            self.set2['heap_blks_hit'] = heap_blks_hit

            self.val[self.vars[0]] = clean
            self.val[self.vars[1]] = backend
            self.val[self.vars[2]] = alloc
            rd = (self.set2['heap_blks_read']-self.set1['heap_blks_read'])
            self.val['heap_blks_read'] = rd
            hd = (self.set2['heap_blks_hit']-self.set1['heap_blks_hit'])
            self.val['heap_blks_hit'] = hd
            self.val['ratio_hit'] = int(hd)*1.0 / (int(hd)+int(rd)+0.00001)
            # dbsize
            c.execute("select sum(pg_database_size(oid)) from pg_database;")
            self.set2['dbsize'] = float(c.fetchone()[0])
            c.execute(
                'select sum(tup_inserted),sum(tup_updated),sum(tup_deleted) from pg_stat_database;')
            records = c.fetchone()
            for k, v in zip(['inserted', 'updated', 'deleted'], records):
                self.set2[k] = float(v)
            self.val['dbsize'] = self.set2['dbsize']
            self.val['grow_rate'] = (
                self.set2['dbsize'] - self.set1['dbsize']) * 1.0 / elapsed
            self.val['inserted'] = (
                self.set2['inserted'] - self.set1['inserted']) * 1.0 / elapsed
            self.val['updated'] = (
                self.set2['updated'] - self.set1['updated']) * 1.0 / elapsed
            self.val['deleted'] = (
                self.set2['deleted'] - self.set1['deleted']) * 1.0 / elapsed
            # transactions
            c.execute(
                'SELECT sum(xact_commit),sum(xact_rollback) FROM pg_stat_database;')
            commit, rollback = c.fetchone()
            self.val['commit'] = commit-self.last_commit
            self.val['rollback'] = rollback-self.last_rollback
            self.last_commit = commit
            self.last_rollback = rollback

            if step == op.delay:
                self.set1.update(self.set2)

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
