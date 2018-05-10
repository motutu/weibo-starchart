#!/usr/bin/env python3

import urllib.parse

import arrow
import requests


def main():
    chart_date = arrow.now().to('Asia/Shanghai').shift(days=-1, hours=-10).date()
    image_dir = chart_date.strftime('https://stats.momo0v0.club/weibo-starchart/%Y/%m/%d/')
    image1 = urllib.parse.urljoin(image_dir, 'cmp.png')
    image2 = urllib.parse.urljoin(image_dir, 'group.png')
    requests.post('http://a.zhim.i.ng:5700/send_group_msg', json={
        'group_id': 540141579,
        'message': [
            {
                'type': 'text',
                'data': {
                    'text': '%s明星势力榜' % chart_date.strftime('%-m月%-d日'),
                },
            },
            {
                'type': 'image',
                'data': {
                    'file': image1,
                },
            },
            {
                'type': 'image',
                'data': {
                    'file': image2,
                },
            },
        ],
    })


if __name__ == '__main__':
    main()
