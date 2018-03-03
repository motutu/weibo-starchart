#!/usr/bin/env python3

import collections
import configparser
import io
import json
import logging
import pathlib
import re
import urllib.parse

import arrow
import requests

import render


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

session = requests.Session()

HERE = pathlib.Path(__file__).resolve().parent
CHART_DATE = arrow.now().to('Asia/Shanghai').shift(days=-1, hours=-10).date()
DATADIR = HERE / 'data' / CHART_DATE.strftime('%Y%m%d')
DATADIR.mkdir(parents=True, exist_ok=True)

Account = collections.namedtuple('Account', 'name, uid, chart_id')
ACCOUNTS = [
    Account('莫寒', 3053424305, 6),
    Account('李艺彤', 3700233717, 5),
    Account('黄婷婷', 3668822213, 6),
    Account('冯薪朵', 3675868752, 6),
    Account('陆婷', 3669120105, 6),
    Account('赵粤', 3668829440, 6),
    Account('张语格', 3050783091, 5),
    Account('许佳琪', 3050737061, 6),
    Account('戴萌', 3050709151, 6),
    Account('孔肖吟', 3058127927, 6),
    Account('林思意', 3675865547, 6),
    Account('吴哲晗', 3050731261, 6),
    Account('李宇琪', 3050792913, 6),
]

CONFIG_FILE = HERE / 'config.ini'
config = configparser.ConfigParser()
config.read([CONFIG_FILE])

QUERY_PARAMS = dict(config.items('query_params'))


def get_individual_chart(account):
    url = 'https://api.weibo.cn/2/cardlist'
    params = QUERY_PARAMS
    params['containerid'] = f'231343_{account.uid}_{account.chart_id}'
    logger.info('GET %s?%s', url, urllib.parse.urlencode(params))
    r = session.get(url, params=params, timeout=5)
    obj = r.json()
    with open(DATADIR / f'{account.name}.json', 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, ensure_ascii=False, sort_keys=True, indent=2)
    return obj


def _normalize_output(s):
    return s.strip().replace('：', ':')


def _normalize_name(s):
    return s.strip().replace('SNH48', '').replace('-', '').replace('_', '')


def parse_individual_chart(name, obj):
    buf = io.StringIO()

    def walk(o):
        if isinstance(o, dict):
            if 'screen_name' in o and name in o['screen_name']:
                if 'verified_type_ext' in o:
                    goldv = o['verified_type_ext'] == 1
                    print('状态:{}'.format('金V' if goldv else '黄V'), file=buf)

                if 'followers_count' in o:
                    followers_count = o['followers_count']
                    if followers_count > 0:
                        print(f'粉丝:{followers_count}', file=buf)

                if 'friends_count' in o:
                    following_count = o['friends_count']
                    if following_count > 0:
                        print(f'关注:{following_count}', file=buf)

            if 'rank' in o and 'user' in o and 'data' in o:
                rank = o['rank']
                user = o['user']
                if name in user.get('screen_name', ''):
                    print(f'新星榜排名:{rank}', file=buf)

            if 'item_desc' in o and 'item_title' in o:
                print('%s:%s' % (o['item_desc'], o['item_title']), file=buf)

            if 'title_sub' in o:
                title_sub = _normalize_output(o['title_sub'])
                if title_sub:
                    print(title_sub, file=buf)

            if 'desc_extr' in o:
                desc_extr = _normalize_output(o['desc_extr'])
                print(o['desc_extr'], file=buf)

            for k in o:
                walk(o[k])
        elif isinstance(o, list):
            for v in o:
                walk(v)
        else:
            return

    print(f'成员:{name}', file=buf)
    walk(obj)
    s = buf.getvalue()
    assert len(s.splitlines()) == 28
    with open(DATADIR / f'{name}.txt', 'w', encoding='utf-8') as fp:
        fp.write(s)

    parsed = collections.OrderedDict([line.split(':') for line in s.splitlines()])
    return parsed


def get_group_chart():
    url = 'https://api.weibo.cn/2/cardlist'
    params = QUERY_PARAMS
    params['containerid'] = '231343_2689280541_8'
    logger.info('GET %s?%s', url, urllib.parse.urlencode(params))
    r = session.get(url, params=params, timeout=5)
    obj = r.json()
    with open(DATADIR / 'group.json', 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, ensure_ascii=False, sort_keys=True, indent=2)
    return obj


def parse_group_chart(obj):
    buf = io.StringIO()

    def walk(o):
        if isinstance(o, dict):
            if 'rank' in o and 'user' in o and 'data' in o:
                rank = o['rank']
                name = _normalize_name(o['user'].get('screen_name', ''))
                contrib = _normalize_output(o['data'])
                print(file=buf)
                print(f'排名:{rank}', file=buf)
                print(f'成员:{name}', file=buf)
                print(contrib, file=buf)

            if 'item_desc' in o and 'item_title' in o:
                if not o['item_desc'].startswith('去'):
                    print('%s:%s' % (o['item_desc'], o['item_title']), file=buf)

            if 'title_sub' in o:
                title_sub = _normalize_output(o['title_sub'])
                if title_sub:
                    print(title_sub, file=buf)

            for k in o:
                walk(o[k])
        elif isinstance(o, list):
            for v in o:
                walk(v)
        else:
            return

    walk(obj)
    s = buf.getvalue()
    with open(DATADIR / 'group.txt', 'w', encoding='utf-8') as fp:
        fp.write(s)

    blocks = [block.strip() for block in re.split('\n\n', s)]
    parsed = [collections.OrderedDict([line.split(':') for line in block.splitlines()])
              for block in blocks]
    return parsed


def main():
    tables = []
    for account in ACCOUNTS:
        obj = get_individual_chart(account)
        tables.append(parse_individual_chart(account.name, obj))

    with open(DATADIR / 'cmp.csv', 'w', encoding='utf-8') as fp:
        for key in tables[0]:
            print(key, end='', file=fp)
            for table in tables:
                print(',%s' % table[key], end='', file=fp)
            print(file=fp)

    obj = get_group_chart()
    ranked_list = parse_group_chart(obj)

    with open(DATADIR / 'group.csv', 'w', encoding='utf-8') as fp:
        print(','.join(ranked_list[0].keys()), file=fp)
        for entry in ranked_list:
            print(','.join(entry.values()), file=fp)

    for index, entry in enumerate(ranked_list):
        if entry['成员'] == '莫寒':
            mohan_rank = index + 1
            break
    else:
        mohan_rank = 0

    with open(DATADIR / 'rendered.html', 'w', encoding='utf-8') as fp:
        fp.write(render.render_csvs([
            ('cmp', DATADIR / 'cmp.csv', dict(
                vertical_header=True,
                highlighted_rows=(1, 5, 11, 16, 21, 25),
                thick_bordered_rows=(5, 10, 15, 20, 24)
            )),
            ('group', DATADIR / 'group.csv', dict(
                cutoff_row=16,
                highlighted_rows=(mohan_rank,),
            )),
        ]))


if __name__ == '__main__':
    main()
