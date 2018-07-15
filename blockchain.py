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
from time import time
import hashlib
import json

class Blockchain:
    def __init__(self):             #每个类中都应该包含一个构造函数
        self.chain = []             #这个数组中每个元素就是一个块
        self.current_transactions = []      #数组存储当前交易的信息

        # 创建创世块，proof随便写。这个区块不用计算，因为里面没有任何内容
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash = None):            #添加块的方法
        block = {
            "index": len(self.chain) + 1,
            "timestamp":time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.last_block)  #chain[-1]表示最后一个数组元素（区块）
        }
        self.current_transactions = []                  #因为已经打包成区块了，所以当前交易就要清空
        self.chain.append(block)                        #把刚打包好的区块加入到链条中
        return block

    def new_transaction(self,sender,recipient,amount) -> int:      #新添加一个区块
        self.current_transactions.append(
            {
                "sender":sender,
                "recipient": recipient,
                "amount": amount,
            }
        )
        return self.last_block['index'] + 1

    @property
    def last_block(self):           #最后一个区块
        return self.chain(-1)

    @staticmethod
    def hash(block):                 #计算区块的哈希值
        block_string = json.dumps(block,sort_keys = True)       #将json转化为字符串数组
        return hashlib.sha256(block_string).hexdigest()            #得到摘要信息