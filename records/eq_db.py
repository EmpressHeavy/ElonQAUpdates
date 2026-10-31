#!/usr/bin/env python3
"""ElonQA source library + answer log (DOGE doge_db.py pattern, generic, data-free).
DB: $EQ_DB or /workspace/elonqa/sources.db; backup dir: $EQ_BACKUP or ./backup next to the DB.
Every quote stored here is VERBATIM text copied from a source opened this session, with its exact locator.
  init | add-source | add-quote | find TEXT | show-source ID | cite QUOTE_ID | log-answer | unknown-log | stats | export-csv DIR | restore DIR | backup
Writes auto-back up (CSV + DB copy; git commit+push if the backup dir is a git repo with a remote). restore is additive."""
import argparse, sqlite3, csv, os, sys, shutil, subprocess, datetime as dt
DB = os.environ.get('EQ_DB', '/workspace/elonqa/sources.db')
BK = os.environ.get('EQ_BACKUP', os.path.join(os.path.dirname(os.path.abspath(DB)), 'backup'))
KINDS = ('x_post', 'book', 'interview', 'article', 'talk', 'filing', 'other')
SCHEMA = """create table sources(id integer primary key, kind text not null, title text not null, author text, published text,
  url text, publisher text, x_post_id text, accessed text, notes text, unique(kind, title, url));
create table quotes(id integer primary key, source_id integer not null references sources(id), text text not null,
  locator text, speaker text default 'Elon Musk', is_paraphrase integer default 0, verified_on text, unique(source_id, text));
create table answers(id integer primary key, ts text, question text, status text check(status in ('answered','unknown','partial')),
  quote_ids text, note text);
create table meta(k text primary key, v text)"""
con = lambda: sqlite3.connect(DB)
now = lambda: dt.datetime.now().isoformat(timespec='seconds')
def export_csv(out):
    os.makedirs(out, exist_ok=True); c = con()
    for (t,) in c.execute("select name from sqlite_master where type='table'").fetchall():
        cur = c.execute(f'select * from {t}')
        with open(os.path.join(out, f'{t}.csv'), 'w', newline='') as f:
            w = csv.writer(f); w.writerow([x[0] for x in cur.description]); w.writerows(cur)
    c.close(); return out
def backup(msg):
    export_csv(BK); shutil.copy2(DB, os.path.join(BK, 'sources.db'))
    if not os.path.isdir(os.path.join(BK, '.git')): return
    g = lambda *a: subprocess.run(['git', '-C', BK, *a], capture_output=True, text=True)
    if not g('remote').stdout.strip(): return
    g('add', '-A')
    if g('diff', '--cached', '--quiet').returncode == 0: return
    g('commit', '-m', msg)
    for _ in range(3):
        r = g('push', 'origin', 'HEAD')
        if r.returncode == 0: print('backup pushed'); return
    print('WARNING: backup push failed (tell the owner): ' + r.stderr.strip(), file=sys.stderr)
def write(fn):
    def w(a):
        c = con(); msg = fn(c, a); c.commit(); c.close(); print(msg); backup(msg)
    return w
def init(a):
    os.makedirs(os.path.dirname(os.path.abspath(DB)), exist_ok=True); c = con()
    for st in SCHEMA.split(';'):
        st = st.strip()
        if st: c.execute(st.replace('create table ', 'create table if not exists ', 1))
    c.execute("insert or ignore into meta values('schema_version','1')"); c.commit(); c.close(); print('db ready:', DB)
@write
def add_source(c, a):
    if a.kind not in KINDS: sys.exit('kind must be one of ' + ','.join(KINDS))
    if a.kind == 'x_post' and not (a.url or a.x_post_id): sys.exit('x_post needs --url or --x-post-id')
    r = c.execute('select id from sources where kind=? and title=? and coalesce(url,"")=coalesce(?,"")', (a.kind, a.title, a.url)).fetchone()
    if r: return 'source exists: %d' % r[0]
    i = c.execute('insert into sources(kind,title,author,published,url,publisher,x_post_id,accessed,notes) values(?,?,?,?,?,?,?,?,?)',
                  (a.kind, a.title, a.author, a.published, a.url, a.publisher, a.x_post_id, now(), a.notes)).lastrowid
    return 'source added: %d' % i
@write
def add_quote(c, a):
    if not c.execute('select 1 from sources where id=?', (a.source,)).fetchone(): sys.exit('no such source')
    if not a.locator: sys.exit('--locator is required (post id/date, page or chapter, timestamp)')
    r = c.execute('select id from quotes where source_id=? and text=?', (a.source, a.text)).fetchone()
    if r: return 'quote exists: %d' % r[0]
    i = c.execute('insert into quotes(source_id,text,locator,speaker,is_paraphrase,verified_on) values(?,?,?,?,?,?)',
                  (a.source, a.text, a.locator, a.speaker, 1 if a.paraphrase else 0, now())).lastrowid
    return 'quote added: %d' % i
def find(a):
    c = con(); q = '%' + a.text + '%'
    for r in c.execute("""select q.id,s.kind,s.title,coalesce(s.published,''),q.locator,q.is_paraphrase,q.text,coalesce(s.url,'')
        from quotes q join sources s on s.id=q.source_id where q.text like ? or s.title like ? or s.notes like ? order by s.published desc limit ?""", (q, q, q, a.limit)):
        print('Q%s | %s | %s | %s | %s | %s | %s | %s' % (r[0], r[1], r[2], r[3], r[4], 'PARAPHRASE' if r[5] else 'verbatim', r[6], r[7]))
def show_source(a):
    c = con(); r = c.execute('select * from sources where id=?', (a.id,)).fetchone()
    if not r: sys.exit('no such source')
    print('|'.join(map(str, r)))
    for q in c.execute('select id,locator,is_paraphrase,text from quotes where source_id=?', (a.id,)): print('  Q%s [%s]%s %s' % (q[0], q[1], ' (paraphrase)' if q[2] else '', q[3]))
def cite(a):
    c = con(); r = c.execute("""select q.text,q.is_paraphrase,q.locator,s.kind,s.title,s.author,s.published,s.url,s.publisher
        from quotes q join sources s on s.id=q.source_id where q.id=?""", (a.id,)).fetchone()
    if not r: sys.exit('no such quote')
    t, para, loc, kind, title, au, pub, url, pubr = r
    body = ('Paraphrase: ' + t) if para else '"%s"' % t
    src = {'x_post': 'Elon Musk on X', 'book': '%s, %s' % (title, au or ''), 'interview': 'Interview: %s' % title}.get(kind, title)
    print('%s\n(%s%s%s%s)' % (body, src, ', ' + pub if pub else '', ', ' + loc if loc else '', ' ' + url if url else ''))
@write
def log_answer(c, a):
    c.execute('insert into answers(ts,question,status,quote_ids,note) values(?,?,?,?,?)', (now(), a.question, a.status, a.quotes, a.note))
    return 'answer logged (%s)' % a.status
def unknown_log(a):
    for r in con().execute("select ts,question,note from answers where status!='answered' order by id desc limit ?", (a.limit,)): print(' | '.join(map(str, r)))
def stats(a):
    c = con()
    for k, n in c.execute('select kind,count(*) from sources group by kind'): print('sources.%s=%d' % (k, n))
    print('quotes=%d answers=%d unknown=%d' % (c.execute('select count(*) from quotes').fetchone()[0], c.execute('select count(*) from answers').fetchone()[0],
          c.execute("select count(*) from answers where status!='answered'").fetchone()[0]))
def restore(a):
    """Additive: adds rows from <dir>/<table>.csv that aren't already there. Never deletes or overwrites."""
    init(a); c = con(); n = {}
    for (t,) in c.execute("select name from sqlite_master where type='table'").fetchall():
        f = os.path.join(a.dir, f'{t}.csv')
        if not os.path.exists(f): continue
        with open(f, newline='') as fh:
            r = csv.reader(fh); h = next(r, None); rows = [[v if v != '' else None for v in x] for x in r]
        if not h: continue
        have = {tuple(None if v is None else str(v) for v in y) for y in c.execute(f'select {",".join(h)} from {t}')}
        add = [x for x in rows if tuple(x) not in have]
        before = c.total_changes
        c.executemany(f'insert or ignore into {t}({",".join(h)}) values({",".join("?" * len(h))})', add); n[t] = c.total_changes - before
    c.commit(); c.close(); print('restored (added, existing kept):', n)
def main():
    ap = argparse.ArgumentParser(); s = ap.add_subparsers(dest='cmd', required=True)
    s.add_parser('init')
    p = s.add_parser('add-source'); p.add_argument('kind'); p.add_argument('title'); p.add_argument('--author'); p.add_argument('--published')
    p.add_argument('--url'); p.add_argument('--publisher'); p.add_argument('--x-post-id', dest='x_post_id'); p.add_argument('--notes')
    p = s.add_parser('add-quote'); p.add_argument('source', type=int); p.add_argument('text'); p.add_argument('--locator', required=True)
    p.add_argument('--speaker', default='Elon Musk'); p.add_argument('--paraphrase', action='store_true')
    p = s.add_parser('find'); p.add_argument('text'); p.add_argument('--limit', type=int, default=15)
    p = s.add_parser('show-source'); p.add_argument('id', type=int)
    p = s.add_parser('cite'); p.add_argument('id', type=int)
    p = s.add_parser('log-answer'); p.add_argument('question'); p.add_argument('--status', default='answered', choices=['answered', 'unknown', 'partial'])
    p.add_argument('--quotes', default=''); p.add_argument('--note', default='')
    p = s.add_parser('unknown-log'); p.add_argument('--limit', type=int, default=20)
    s.add_parser('stats')
    p = s.add_parser('export-csv'); p.add_argument('dir')
    p = s.add_parser('restore'); p.add_argument('dir')
    s.add_parser('backup')
    a = ap.parse_args()
    if a.cmd != 'init' and not os.path.exists(DB): init(a)
    {'init': init, 'add-source': add_source, 'add-quote': add_quote, 'find': find, 'show-source': show_source, 'cite': cite,
     'log-answer': log_answer, 'unknown-log': unknown_log, 'stats': stats, 'export-csv': lambda a: print(export_csv(a.dir)),
     'restore': restore, 'backup': lambda a: (backup('manual backup'), print('backed up to', BK))}[a.cmd](a)
if __name__ == '__main__': main()
