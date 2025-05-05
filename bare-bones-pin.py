
from bsky_utils import *


def main():
    load_dotenv()
    handle, did, session, service = credentials()

    _, _, pinboard_rkey = decompose_uri(create_record(
        session, service, {'$type': 'xyz.jeroba.tags.tag', 'title': '📌'})
    )

    apply_writes_batch(session, service, [{
        'tag': pinboard_rkey,
        '$type': 'xyz.jeroba.tags.tagged',
        'record': uri
    } for uri in traverse(
        search_posts_from_me('📌', session, service),
        ['record', 'reply', 'parent', 'uri'],
        get_all=True)
    ])

    print(f'https://pinboards.jeroba.xyz/profile/{did}/board/{pinboard_rkey}')


if __name__ == "__main__":
    main()


