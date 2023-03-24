class dstat_plugin(dstat):
    """
    Plugin for PostgreSQL connections.
    """

    def __init__(self):
        self.name = 'postgresql settings'
        self.nick = ('shared_buffers',
                     'work_mem', 'bgwriter_delay',
                     'max_connections',
                     'autovacuum_work_mem',
                     'temp_buffers', 'autovacuum_max_workers',
                     'maintenance_work_mem', 'checkpoint_timeout',
                     'max_wal_size', 'checkpoint_completion_target',
                     'wal_keep_segments', 'wal_segment_size')
        self.vars = self.nick
        self.type = 'f'
        self.width = 9
        self.scale = 1

    def check(self):
        pass

    def extract(self):
        from conn import PostgresqlConn
        try:
            with PostgresqlConn() as c:
                #  c = self.db.cursor()
                sql = 'select name, setting from pg_settings where name in {}; '
                sql = sql.format(self.vars)
                c.execute(sql)
                res = c.fetchall()

                for k, v in res:
                    v = float(v)
                    self.val[k] = v

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
