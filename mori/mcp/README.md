# MCP集成说明

## 什么是MCP？

MCP (Model Context Protocol) 是一个用于连接AI应用与外部工具和数据源的协议。通过MCP，Mori可以访问更多的工具和资源。

## 当前状态

⚠️ **MCP功能目前处于预留状态，尚未实现。**

## 未来计划

在后续版本中，我们计划实现以下MCP功能：

1. **MCP客户端** - 连接到MCP服务器
2. **工具集成** - 自动将MCP工具注册到Toolkit
3. **资源访问** - 访问MCP服务器提供的资源
4. **提示词管理** - 使用MCP提供的提示词模板

## 如何使用（未来）

```python
# 未来的使用示例
from mori.mcp import MCPClient

# 创建MCP客户端
mcp_client = MCPClient("config/mcp.json")

# 连接到MCP服务器
await mcp_client.connect()

# 获取可用工具
tools = await mcp_client.list_tools()

# 将MCP工具注册到Toolkit
toolkit = Toolkit()
mcp_client.register_tools(toolkit)
```

## 参考资料

- [AgentScope MCP文档](https://doc.agentscope.io/tutorial/task_mcp.html)
- [MCP官方文档](https://modelcontextprotocol.io/)

## 贡献

如果你有兴趣实现MCP功能，欢迎提交PR！
