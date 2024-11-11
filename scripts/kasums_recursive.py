class Post:
    def __init__(self,post,replies=[]):
        self.post = post
        self.replies = replies


def read_tree(post):
    list_o_replies=[post.post]
    if post.replies:
        for reply in post.replies:
            list_o_replies.extend(read_tree(reply))
    return list_o_replies


if __name__=="__main__": 
    post_C1=Post("henlo")
    post_C2=Post("hewwo")
    post_B1=Post("hihi",replies=[post_C1,post_C2]) 
    post_B2=Post("hewy") 
    post_A=Post("hi",replies=[post_B1,post_B2]) 
    none_guy=None
    friendly_guy="i'm friendly"
    print(friendly_guy in none_guy)
    print(read_tree(post_A))
