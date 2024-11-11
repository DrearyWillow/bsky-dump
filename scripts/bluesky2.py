from .common import InfoExtractor
from ..utils import mimetype2ext, parse_iso8601, traverse_obj, url_or_none

import json

class BlueskyIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?bsky\.app/profile/(?P<handle>[^/]+)/post/(?P<id>[0-9a-zA-Z]+)'
    _TESTS = [{
        'url': 'https://bsky.app/profile/blu3blue.bsky.social/post/3l4omssdl632g',
        'md5': '375539c1930ab05d15585ed772ab54fd',
        'info_dict': {
            'id': '3l4omssdl632g',
            'ext': 'mp4',
            'title': 'Blu3Blu3Lilith: OMG WE HAVE VIDEOS NOW',
            'upload_date': '20240921',
            'description': 'OMG WE HAVE VIDEOS NOW',
            'thumbnail': r're:^https?://.*\.jpg$',
            'alt-title': None,
            'uploader': 'Blu3Blu3Lilith',
            'channel': 'blu3blue.bsky.social',
            'uploader_id': 'did:plc:pzdr5ylumf7vmvwasrpr5bf2',
            'channel_id': 'did:plc:pzdr5ylumf7vmvwasrpr5bf2',
            'uploader_url': r're:^https?://.*',
            'channel_url': r're:^https?://.*',
            'timestamp': 1726940605,
            'like_count': int,
            'repost_count': int,
            'comment_count': int,
            'webpage_url': r're:^https?://.*',
            'tags': 'count:1',
            'subtitles': 'count:0',
            'comments': list, # 'count:28'
        },
    }, {
        'url': 'https://bsky.app/profile/bsky.app/post/3l3vgf77uco2g',
        'md5': 'b9e344fdbce9f2852c668a97efefb105',
        'info_dict': {
            'id': '3l3vgf77uco2g',
            'ext': 'mp4',
            'title': r're:^Bluesky: Bluesky now has video!',
            'upload_date': '20240911',
            'description': r're:^Bluesky now has video!',
            'thumbnail': r're:^https?://.*\.jpg$',
            'alt-title': 'Bluesky video feature announcement',
            'uploader': 'Bluesky',
            'channel': 'bsky.app',
            'uploader_id': 'did:plc:z72i7hdynmk6r22z27h6tvur',
            'channel_id': 'did:plc:z72i7hdynmk6r22z27h6tvur',
            'uploader_url': r're:^https?://.*',
            'channel_url': r're:^https?://.*',
            'timestamp': 1726074716,
            'like_count': int,
            'repost_count': int,
            'comment_count': int,
            'webpage_url': r're:^https?://.*',
            'tags': 'count:2',
            'subtitles': dict,  # count:1 if write-subs
            'comments': 'count:1531',
        },
    }, {
        'url': 'https://bsky.app/profile/clockworkbanana.fun/post/3l45kdlktfe2o',
        'md5': 'a426d7b0fc52bc89fc8f59668be3496e',
        'info_dict': {
            'id': '3l45kdlktfe2o',
            'ext': 'mp4',
            'title': r're:^clockwork banana: alright.',
            'upload_date': '20240914',
            'description': r're:^alright.\nthis was .. a tiny bit of a pain.',
            'thumbnail': r're:^https?://.*\.jpg$',
            'alt-title': r're:^me making a goofy little test video',
            'uploader': 'clockwork banana',
            'channel': 'clockworkbanana.fun',
            'uploader_id': 'did:plc:3tndo2mqg2vgpxnpyrxiol6p',
            'channel_id': 'did:plc:3tndo2mqg2vgpxnpyrxiol6p',
            'uploader_url': r're:^https?://.*',
            'channel_url': r're:^https?://.*',
            'timestamp': 1726353835,
            'like_count': int,
            'repost_count': int,
            'comment_count': int,
            'webpage_url': r're:^https?://.*',
            'tags': 'count:1',
            'subtitles': dict,  # count:1 if write-subs
            'comments': 'count:13',
        },
    }]

    def _get_subtitles(meta, video_id):
        return self._extract_m3u8_formats_and_subtitles(
                traverse_obj(meta, ('thread', 'post', 'embed', 'playlist')),
                video_id, 'mp4', 'm3u8_native', m3u8_id='hls', fatal=False,
                note='Downloading HD m3u8 information', errnote='Unable to download HD m3u8 information')[1]

    def _get_comments(self, meta):
        yield self.traverse_replies(
            meta.get('thread'),
            (traverse_obj(meta, ('thread', 'post', 'record', 'reply', 'root', 'uri'))
             or traverse_obj(meta, ('thread', 'post', 'uri'))))

    def traverse_replies(self, thread_node, root_uri):
        parent_uri = traverse_obj(thread_node, ('post', 'record', 'reply', 'parent', 'uri'))
        parent_id = 'root' if parent_uri == root_uri else parent_uri
        author_handle = traverse_obj(thread_node, ('post', 'author', 'handle'))
        author_did = traverse_obj(thread_node, ('post', 'author', 'did'))
        yield {
            'id': traverse_obj(thread_node, ('post', 'uri')),
            'text': traverse_obj(thread_node, ('post', 'record', 'text')),
            'timestamp': parse_iso8601(traverse_obj(thread_node, ('post', 'record', 'createdAt'))),
            'parent': parent_id,
            'like_count': traverse_obj(thread_node, ('post', 'likeCount')),
            'author': traverse_obj(thread_node, ('post', 'author', 'displayName')),
            'author_id': author_did,
            'author_thumbnail': traverse_obj(thread_node, ('post', 'author', 'avatar'), expected_type=url_or_none),
            'author_url': f'https://bsky.app/profile/{author_handle}',
            'author_is_uploader': 'Yes' if author_did in root_uri else 'No',
        }
        if replies := thread_node.get('replies'):
            for reply in replies:
                yield from self.traverse_replies(reply, root_uri)

    def _real_extract(self, url):
        handle, video_id = self._match_valid_url(url).groups()
        did = self._download_json(
            'https://bsky.social/xrpc/com.atproto.identity.resolveHandle',
            video_id, query={'handle': handle}, expected_status=200).get('did')

        # if self.get_param('write_comments', False):
        # self.get_param('getcomments')

        # if (self.get_param('writesubtitles', False)
        #         or self.get_param('listsubtitles')):

        # self._configuration_arg('max_comments', [''])[0]
        getcomments = self.get_param('getcomments', True)
        # getcomments = True
        meta = self._download_json(
            'https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread',
            video_id, headers={'Content-Type': 'application/json'},
            query={'uri': f'at://{did}/app.bsky.feed.post/{video_id}',
                   'depth': 1000 if getcomments else 0,
                   'parentHeight': 1000 if getcomments else 0},
            expected_status=200)

        # formatted_comments = self.extract_comments(meta)
        # if formatted_comments != None

        # with open('/home/kyler/Downloads/op.json', 'w') as file:
        #     json.dump(meta, file, indent=4)
        
        # extractor = self.extract_comments(meta)
        #formatted_comments = [[*l] for l in extractor().get('comments')][0]
        # formatted_comments = [*(extractor().get('comments'))[0]]

        # formatted_comments = [*(self.extract_comments(meta)().get('comments'))[0]]
        
        # with open('/home/kyler/Downloads/fc.txt', 'w') as file:
        #     file.write(str(formatted_comments))

        # subs = self.extract_subtitles(meta, video_id)

        # if (self.get_param('writesubtitles', False)
        #     or self.get_param('writeautomaticsub', False)
        #         or self.get_param('listsubtitles')):
        #     _, subs = self._extract_m3u8_formats_and_subtitles(
        #         traverse_obj(meta, ('thread', 'post', 'embed', 'playlist')),
        #         video_id, 'mp4', 'm3u8_native', m3u8_id='hls', fatal=False,
        #         note='Downloading HD m3u8 information', errnote='Unable to download HD m3u8 information')
        # else:
        #     subs = {}

        blob_cid = (traverse_obj(meta, ('thread', 'post', 'embed', 'cid'))
                    or traverse_obj(meta, ('thread', 'post', 'record', 'embed', 'video', 'ref', '$link')))

        formatted_replies = self.traverse_replies(
            meta.get('thread'), (traverse_obj(meta, ('thread', 'post', 'record', 'reply', 'root', 'uri'))
                                 or traverse_obj(meta, ('thread', 'post', 'uri'))))

        uploader = traverse_obj(meta, ('thread', 'post', 'author', 'displayName'))
        description = traverse_obj(meta, ('thread', 'post', 'record', 'text'))

        return {
            'id': video_id,
            'title': f'{uploader}: {description}',
            'url': f'https://bsky.social/xrpc/com.atproto.sync.getBlob?did={did}&cid={blob_cid}',
            'ext': mimetype2ext(traverse_obj(meta, ('thread', 'post', 'record', 'embed', 'video', 'mimeType')), 'mp4'),
            'description': description,
            'thumbnail': traverse_obj(meta, ('thread', 'post', 'embed', 'thumbnail'), expected_type=url_or_none),
            'alt-title': traverse_obj(meta, ('thread', 'post', 'record', 'alt'), ('thread', 'post', 'embed', 'alt')),
            'uploader': uploader,
            'channel': handle,
            'uploader_id': did,
            'channel_id': did,
            'uploader_url': f'https://bsky.app/profile/{handle}',
            'channel_url': f'https://bsky.app/profile/{handle}',
            'timestamp': parse_iso8601(traverse_obj(meta, ('thread', 'post', 'record', 'createdAt'))),
            'like_count': traverse_obj(meta, ('thread', 'post', 'likeCount')),
            'repost_count': traverse_obj(meta, ('thread', 'post', 'repostCount')),
            'comment_count': traverse_obj(meta, ('thread', 'post', 'replyCount')),
            'webpage_url': url,
            'tags': (traverse_obj(meta, ('thread', 'post', 'labels'), expected_type=list)
                     + traverse_obj(meta, ('thread', 'post', 'record', 'langs'), expected_type=list)),
            # 'comments': [] if (formatted_comments := self.extract_comments(meta)) is None else formatted_comments[:1],
            # 'comments': [formatted_comments][:1] if (formatted_comments := self.extract_comments(meta)) else [],
            # 'comments': formatted_comments[1:],
            'comments': [*(self.extract_comments(meta)().get('comments'))[0]][1:],
            'subtitles': self._merge_subtitles(self.extract_subtitles(meta, video_id)),
        }
