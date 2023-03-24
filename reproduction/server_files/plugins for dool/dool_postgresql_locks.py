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
    Plugin for PostgreSQL locks.
    """

    def __init__(self):
        self.name = 'postgresql locks'
        self.nick = ('Dead',)
        self.vars = ('deadlocks',)
        self.type = 'f'
        self.width = 4
        self.scale = 1

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
            c.execute('select sum(deadlocks) from pg_stat_database;')
            self.set2['deadlocks'] = c.fetchone()[0]
            self.val['deadlocks'] = (self.set2['deadlocks'] - self.set1['deadlocks']) * 1.0 / elapsed
            if step == op.delay:
                self.set1.update(self.set2)

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
