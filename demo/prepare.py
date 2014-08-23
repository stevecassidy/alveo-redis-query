from alveo_redis_query import AlveoIndex

if __name__ == '__main__':
    index  = AlveoIndex("place-your-apikey-here")
    index.clear()
    index.index_item_list_by_name("gum-tree")
    print("done")