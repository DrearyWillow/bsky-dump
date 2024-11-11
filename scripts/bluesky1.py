from .common import InfoExtractor
from ..utils import (
    parse_iso8601,
    traverse_obj
)

class BlueskyIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?bsky\.app/profile/(?P<handle>[^/]+)/post/(?P<id>[0-9a-zA-Z]+)'
    _TESTS = [{
        'url': 'https://bsky.app/profile/blu3blue.bsky.social/post/3l4omssdl632g',
        'md5': '067838923631f1ab63b3148b808920cc',
        'info_dict': {
            'id': '3l4omssdl632g',
            'ext': 'mp4',
            'title': str,
            'upload_date': str,
            'description': str,
            'thumbnail': r're:^https?://.*\.jpg$',
            'alt-title': None,
            'uploader': str,
            'channel': str,
            'uploader_id': str,
            'channel_id': str,
            'uploader_url': r're:^https?://.*',
            'channel_url': r're:^https?://.*',
            'timestamp': int,
            'like_count': int,
            'repost_count': None,
            'comment_count': int,
            'webpage_url': r're:^https?://.*',
            'tags': 'count:0',
        }
    }]
    #     ,
    # }, {
    #     # test case: video with different channel and uploader
    #     'url': 'https://bsky.app/profile/dreary.bsky.social/post/3l4372eftjc24',
    #     'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
    #     'info_dict': {
    #         'id': '3l4372eftjc24',
    #         'ext': 'mp4',
    #         # 'title': 'Israel at War | Full Measure',
    #         # 'description': 'md5:38cf7bc6f42da1a877835539111c69ef',
    #         # 'thumbnail': r're:^https?://.*\.jpg$',
    #         # 'uploader': 'sharylattkisson',
    #         # 'upload_date': '20231106',
    #         # 'uploader_url': 'https://www.bitchute.com/profile/9K0kUWA9zmd9/',
    #         # 'channel': 'Full Measure with Sharyl Attkisson',
    #         # 'channel_url': 'https://www.bitchute.com/channel/sharylattkisson/',
    #     }
    # }]

    # def resolve_did(handle):
    #     resolve_url = 'https://bsky.social/xrpc/com.atproto.identity.resolveHandle'
    #     try:
    #         return self._download_json(resolve_url, query={'handle': handle}, expected_status=200).get('did')
    #     # result = requests.get(resolve_url, params={'handle': handle})
    #     # if result.status_code == 200:
    #     #     data = result.json()
    #     #     return data.get('did')
    #     except:
    #         raise ExtractorError(f'Failed to retrieve DID from handle \'{handle}\'.', expected=True)

    # def get_post_thread(did, video_id):
    #     api_url = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread'
    #     headers = {'Content-Type': 'application/json'}
    #     params = {'uri': f"at://{did}/app.bsky.feed.post/{video_id}", 'depth': 0}
    #     try:
    #         return self._download_json(api_url, video_id, headers=headers, query=params, expected_status=200)
    #     # result = self._download_webpage(api_url, headers=headers, params=params)
    #     # result = requests.get(api_url, headers=headers, params=params)
    #     # if result.status_code == 200:
    #     #     return result.json()
    #     except:
    #         raise ExtractorError('Failed to retrieve post thread.', expected=True)

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # handle = self._match_handle(url)
        handle = self._search_regex(self._VALID_URL, url, 'handle', group='handle')
        # did = self.resolve_did(handle)
        resolve_url = 'https://bsky.social/xrpc/com.atproto.identity.resolveHandle'
        did = self._download_json(resolve_url, video_id, query={'handle': handle}, expected_status=200).get('did')

        api_url = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread'
        headers = {'Content-Type': 'application/json'}
        params = {'uri': f"at://{did}/app.bsky.feed.post/{video_id}", 'depth': 0}
        meta = self._download_json(api_url, video_id, headers=headers, query=params, expected_status=200)

        # meta = self.get_post_thread(did, video_id)

        # TODO more code goes here, for example ...
        # webpage = self._download_webpage(url, video_id)
        # title = self._html_search_regex(r'<h1>(.+?)</h1>', webpage, 'title')

        m3u8_url = traverse_obj(meta, ("thread", "post", "embed", "playlist"))

        uploader = traverse_obj(meta, ("thread", "post", "author", "displayName"))
        description = traverse_obj(meta, ("thread", "post", "record", "text"))

        return {
            'id': video_id,
            'title': f"{uploader}: {description}",
            'formats': self._extract_m3u8_formats(
                m3u8_url, video_id, 'mp4', 'm3u8_native', m3u8_id='hls',
                note='Downloading HD m3u8 information', errnote='Unable to download HD m3u8 information'),
            'description': description,
            'thumbnail': traverse_obj(meta, ("thread", "post", "embed", "thumbnail")),
            'alt-title': traverse_obj(meta, ("thread", "post", "record", "alt")) or traverse_obj(meta, ("thread", "post", "embed", "alt")),
            'uploader': uploader,
            'channel': uploader,
            'uploader_id': handle,
            'channel_id': handle,
            'uploader_url': f"https://bsky.app/profile/{handle}",
            'channel_url': f"https://bsky.app/profile/{handle}",
            'timestamp': parse_iso8601(traverse_obj(meta, ("thread", "post", "record", "createdAt"))),
            'like_count': traverse_obj(meta, ("thread", "post", "likeCount")),
            'repost_count': traverse_obj(meta, ("thread", "post", "respostCount")),
            'comment_count': traverse_obj(meta, ("thread", "post", "replyCount")),
            'webpage_url': url,
            'tags': traverse_obj(meta, ("thread", "post", "labels")), #idk
            # 'comments': 
            # 'subtitles': 
        }
