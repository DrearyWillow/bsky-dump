

def fetch_page(api, params, cursor=None):
    params['cursor'] = cursor
    return safe_request('get', api, params=params)

def generic_page_loop(api, page_limit, path_to_output, path_to_cursor, **kwargs):
    params = {**kwargs, 'limit': page_limit}

    res = fetch_page(api, params)
    output = traverse(res, path_to_output)

    while traverse(res, path_to_cursor):
        res = fetch_page(api, params, traverse(res, path_to_cursor))
        output.extend(traverse(res, path_to_output))
    return output

def get_post_quotes(at_uri):
    api = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getQuotes'
    if at_uri.startswith("http"): at_uri = url2uri(at_uri)
    params={'uri': at_uri}
    return generic_page_loop(api, 100, ['posts'], ['cursor'], **params)
