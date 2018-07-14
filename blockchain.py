#一个区块的结构如下：
# {
#     "index":0,      #区块的索引
#     "timestamp":"",
#     "transactions":[
#         {
#             "sender":"",
#             "recipient":"",
#             "amount":5,
#         }
#     ],
#     "proof":"",     #工作量证明
#     "previous_hash":"",     #上一个区块的哈希值
# }

class Blockchain:
    def __init__(self):             #每个类中都应该包含一个构造函数
        self.chain = []             #这个数组中每个元素就是一个块
        self.current_transactions = []      #数组存储当前交易的信息

    def new_block(self):            #添加块的方法
        pass

    def new_transaction(self):      #新添加一个区块
        pass

    @staticmethod                    #声明为静态方法
    def hash(block):                 #计算区块的哈希值
        pass

    @property
    def last_block(self):           #最后一个区块
        pass