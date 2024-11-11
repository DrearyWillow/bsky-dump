


def fetch_page(api, params, cursor=None):
    params['cursor'] = cursor
    return safe_request('get', api, params=params)

def generic_page_loop(api, page_limit, path_to_output, path_to_cursor, **kwargs):
    # TODO: try out yield maybe?
    params = {**kwargs, 'limit': page_limit}

    res = fetch_page(api, params)
    output = traverse(res, path_to_output)

    # not super reliable `and` condition because sometimes there are deactivated records
    # so i'm just relying on cursor being None
    while traverse(res, path_to_cursor): #and (len(traverse(res, path_to_output)) >= page_limit):
        res = fetch_page(api, params, traverse(res, path_to_cursor))
        output.extend(traverse(res, path_to_output))
    return output

def get_post_quotes(at_uri):
    api = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getQuotes'
    params={'uri': at_uri}
    return generic_page_loop(api, 100, ['posts'], ['cursor'], **params)


# logic stolen shamelessly from jules
# https://github.com/notjuliet/cleanfollow-bsky/blob/main/src/App.tsx#L193

# const fetchHiddenAccounts = async () => {
#     const fetchFollows = async () => {
#       const PAGE_LIMIT = 100;
#       const fetchPage = async (cursor?: string) => {
#         return await rpc.get("com.atproto.repo.listRecords", {
#           params: {
#             repo: agent.sub,
#             collection: "app.bsky.graph.follow",
#             limit: PAGE_LIMIT,
#             cursor: cursor,
#           },
#         });
#       };

#       let res = await fetchPage();
#       let follows = res.data.records;

#       while (res.data.cursor && res.data.records.length >= PAGE_LIMIT) {
#         res = await fetchPage(res.data.cursor);
#         follows = follows.concat(res.data.records);
#       }

#       return follows;
#     };

#     setProgress(0);
#     setNotice("");

#     const follows = await fetchFollows();
#     setFollowCount(follows.length);
#     const tmpFollows: FollowRecord[] = [];

#     follows.forEach(async (record) => {
#       let status: RepoStatus | undefined = undefined;
#       const follow = record.value as AppBskyGraphFollow.Record;
#       let handle = "";

#       try {
#         const res = await rpc.get("app.bsky.actor.getProfile", {
#           params: { actor: follow.subject },
#         });

#         handle = res.data.handle;
#         const viewer = res.data.viewer!;

#         if (!viewer.followedBy) status = RepoStatus.NONMUTUAL;

#         if (viewer.blockedBy) {
#           status =
#             viewer.blocking || viewer.blockingByList ?
#               RepoStatus.BLOCKEDBY | RepoStatus.BLOCKING
#             : RepoStatus.BLOCKEDBY;
#         } else if (res.data.did.includes(agent.sub)) {
#           status = RepoStatus.YOURSELF;
#         } else if (viewer.blocking || viewer.blockingByList) {
#           status = RepoStatus.BLOCKING;
#         }
#       } catch (e: any) {
#         handle = await resolveDid(follow.subject);

#         status =
#           e.message.includes("not found") ? RepoStatus.DELETED
#           : e.message.includes("deactivated") ? RepoStatus.DEACTIVATED
#           : e.message.includes("suspended") ? RepoStatus.SUSPENDED
#           : undefined;
#       }

#       const status_label =
#         status == RepoStatus.DELETED ? "Deleted"
#         : status == RepoStatus.DEACTIVATED ? "Deactivated"
#         : status == RepoStatus.SUSPENDED ? "Suspended"
#         : status == RepoStatus.NONMUTUAL ? "Non Mutual"
#         : status == RepoStatus.YOURSELF ? "Literally Yourself"
#         : status == RepoStatus.BLOCKING ? "Blocking"
#         : status == RepoStatus.BLOCKEDBY ? "Blocked by"
#         : RepoStatus.BLOCKEDBY | RepoStatus.BLOCKING ? "Mutual Block"
#         : "";

#       if (status !== undefined) {
#         tmpFollows.push({
#           did: follow.subject,
#           handle: handle,
#           uri: record.uri,
#           status: status,
#           status_label: status_label,
#           toDelete: false,
#           visible: status != RepoStatus.NONMUTUAL,
#         });
#       }
#       setProgress(progress() + 1);
#       if (progress() == followCount()) setFollowRecords(tmpFollows);
#     });
#   };