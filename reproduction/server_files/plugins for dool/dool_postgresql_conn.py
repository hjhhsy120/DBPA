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
        self.name = 'postgresql conn'
        self.nick = ('Conn', '%Con',
                     'Act', 'LongQ',
                     'LongX', 'Idl',
                     'LIdl', 'LWait',
                     'SQLs1', 'SQLs3',
                     'SQLs5', 
                     'Xact1', 'Xact3',
                     )
        self.vars = ('conn_cnt', 'conn_cnt_rate',
                     'conn_active_cnt', 'long_query_cnt',
                     'long_transaction_cnt', 'idl_cnt',
                     'long_idl_cnt', 'long_waiting_cnt',
                     'sqls_1sec', 'sqls_3sec',
                     'sqls_5sec',
                     'transactions_1sec', 'transactions_3sec',
                     )
        self.type = 'f'
        self.width = 5
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
            c.execute("select count(*) used from pg_stat_activity")
            conn_cnt = c.fetchone()[0]
            c.execute(
                "select setting::int max_conn from pg_settings where name=$$max_connections$$")
            max_conn = c.fetchone()[0]
            c.execute(
                "select setting::int res_for_super from pg_settings where name=$$superuser_reserved_connections$$")
            res_for_super_conn = c.fetchone()[0]
            c.execute(
                "select count(*) from pg_stat_activity where state = 'active'")
            conn_cnt_activate = c.fetchone()[0]

            c.execute(
                "select count(*) from pg_stat_activity where state = 'active' and now()-query_start > interval '15 second';")
            long_query_cnt = c.fetchone()[0]

            c.execute(
                "select count(*) from pg_stat_activity where now()-xact_start > interval '15 second';")
            long_transaction_cnt = c.fetchone()[0]

            c.execute(
                "select count(*) from pg_stat_activity where state='idle in transaction'")
            idl_cnt = c.fetchone()[0]
            c.execute(
                "select count(*) from pg_stat_activity where state='idle in transaction' and now()-state_change > interval '15 second';")
            long_idl_cnt = c.fetchone()[0]

            c.execute(
                "select count(*) from pg_stat_activity where wait_event_type is not null and now()-state_change > interval '15 second';")
            long_waiting_cnt = c.fetchone()[0]

            c.execute("select count(*) from pg_stat_activity where date_part('epoch',now()-query_start)>1 and state<>'idle';")
            sqls_1sec = c.fetchone()[0]
            c.execute("select count(*) from pg_stat_activity where date_part('epoch',now()-query_start)>3 and state<>'idle';")
            sqls_3sec = c.fetchone()[0]
            c.execute("select count(*) from pg_stat_activity where date_part('epoch',now()-query_start)>5 and state<>'idle';")
            sqls_5sec = c.fetchone()[0]

            c.execute("select count(*) from pg_stat_activity where date_part('epoch',now()-xact_start)>1 and state<>'idle';")
            transactions_1sec = c.fetchone()[0]
            c.execute("select count(*) from pg_stat_activity where date_part('epoch',now()-xact_start)>3 and state<>'idle';")
            transactions_3sec = c.fetchone()[0]

            self.val[self.vars[0]] = conn_cnt
            self.val[self.vars[1]] = conn_cnt/max_conn
            self.val[self.vars[2]] = conn_cnt_activate

            self.val[self.vars[3]] = long_query_cnt
            self.val[self.vars[4]] = long_transaction_cnt
            self.val[self.vars[5]] = idl_cnt
            self.val[self.vars[6]] = long_idl_cnt
            self.val[self.vars[7]] = long_waiting_cnt

            self.val[self.vars[8]] = sqls_1sec
            self.val[self.vars[9]] = sqls_3sec
            self.val[self.vars[10]] = sqls_5sec

            self.val[self.vars[11]] = transactions_1sec
            self.val[self.vars[12]] = transactions_3sec

        except Exception as e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
