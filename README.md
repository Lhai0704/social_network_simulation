# social_network_simulation
## 社交网络模拟系统
LLM驱动节点生成聊天内容

fastapi作为后端框架。MySQL数据持久化。
ollama本地LLM，llama3.1-8b

## 安装
创建config.py文件，输入
```
MYSQLPASSWORD = 'YOUR_PASSWORD'
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:" + MYSQLPASSWORD + "@localhost/social_network_simulation"
```
## 基本操作
### 添加节点
`curl -X POST "http://localhost:8000/nodes/" -H "Content-Type: application/json" -d '{"name": "Amy"}'`
### 添加节点连接
`curl -X POST "http://localhost:8000/nodes/1/connect" \
-H "Content-Type: application/json" \
-d '{"target_node_id": 2}'`
### 两个节点对话
`curl -X POST "http://localhost:8000/start-dialogue/?node1_id=1&node2_id=2&num_turns=5"`
### 所有节点交流
`curl -X POST "http://localhost:8000/multi-dialogue/?num_turns=5"`

## TODO:
可视化
从真实数据中提取节点profile

## 参考资料：
- https://dl.acm.org/doi/abs/10.1145/3586183.3606763
- https://arxiv.org/abs/2307.14984
- https://arxiv.org/abs/2311.09618
