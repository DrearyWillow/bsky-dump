#!/usr/bin/env python

from bsky_utils import *
import sys

def get_clout(thread_node, clout_dict):
    print(thread_node.get('post').get('uri'))
    clout_dict['likes'] += thread_node.get('post').get('likeCount')
    clout_dict['reposts'] += thread_node.get('post').get('repostCount')
    if replies := thread_node.get('replies'):
        for reply in replies:
            clout_dict['replies'] +=  1
            get_clout(reply, clout_dict)
    for quote in get_post_quotes(thread_node.get('post').get('uri')):
        clout_dict['quotes'] += 1
        get_clout(get_post_thread(quote.get('uri')), clout_dict)

def main():
    clout_dict = {'likes': 0, 'reposts': 0, 'replies': 0, 'quotes': 0}
    get_clout(get_post_thread(sys.argv[1]), clout_dict)
    engagements = 0
    for key, value in clout_dict.items():
        print(f'{key}: {value}')
        engagements += value
    print(f"engagements: {engagements}")

if __name__ == "__main__":
    main()