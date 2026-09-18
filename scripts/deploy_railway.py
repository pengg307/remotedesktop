"""
Railway API 客户端
用于自动创建Railway项目和服务
"""
import json
import os
import sys
import urllib.request
import urllib.error

def call_railway_api(api_key: str, query: str, variables: dict = None):
    """调用Railway GraphQL API"""
    url = "https://backboard.railway.com/graphql"
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API错误: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"连接错误: {e}")
        return None


def get_user_info(api_key: str):
    """获取当前用户信息"""
    query = """
    query {
      actor {
        id
        email
        name
      }
    }
    """
    result = call_railway_api(api_key, query)
    if result and 'data' in result:
        return result['data'].get('actor')
    return None


def create_project(api_key: str, name: str) -> str:
    """创建项目，返回project_id"""
    query = """
    mutation CreateProject($name: String!) {
      createProject(input: { name: $name }) {
        id
        name
      }
    }
    """
    result = call_railway_api(api_key, query, {"name": name})
    if result and 'data' in result:
        return result['data']['createProject']['id']
    return None


def main():
    """主函数 - 从环境变量获取API Key并测试"""
    api_key = os.getenv("RAILWAY_API_KEY", "").strip()
    
    if not api_key:
        print("❌ 未找到RAILWAY_API_KEY环境变量")
        print("")
        print("请获取API Key:")
        print("1. 登录 https://railway.com")
        print("2. 进入 Settings → API Keys")
        print("3. 点击 Generate New Token")
        print("4. 复制Token")
        print("")
        print("然后设置环境变量:")
        print("  export RAILWAY_API_KEY='your-token-here'  (Linux/Mac)")
        print("  set RAILWAY_API_KEY=your-token-here        (Windows CMD)")
        print("  $env:RAILWAY_API_KEY='your-token-here'     (PowerShell)")
        print("")
        print("或者在当前命令中直接设置:")
        print("  RAILWAY_API_KEY=xxx python deploy_railway.py")
        sys.exit(1)
    
    print("=" * 60)
    print("  Railway API 测试")
    print("=" * 60)
    print()
    print(f"API Key: {api_key[:20]}...")
    print()
    
    # 测试连接
    user = get_user_info(api_key)
    if user:
        print(f"✅ 连接成功！")
        print(f"   用户: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        print()
        
        # 列出项目
        query = """
        query {
          actor {
            projects(first: 10) {
              edges {
                node {
                  id
                  name
                  environmentName
                  createdAt
                }
              }
            }
          }
        }
        """
        result = call_railway_api(api_key, query)
        if result and 'data' in result:
            projects = result['data']['actor']['projects']['edges']
            if projects:
                print("📁 现有项目:")
                for p in projects:
                    node = p['node']
                    print(f"   • {node['name']} (ID: {node['id'][:8]}...)")
            else:
                print("📁 暂无项目，可以创建新的")
                print()
                new_name = input("输入新项目名称（默认: remotedesk-signaling）: ").strip() or "remotedesk-signaling"
                new_id = create_project(api_key, new_name)
                if new_id:
                    print(f"✅ 创建项目成功: {new_id}")
                else:
                    print("❌ 创建项目失败")
    else:
        print("❌ 认证失败，请检查API Key是否正确")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
