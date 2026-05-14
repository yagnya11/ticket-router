from mcp.server.fastmcp import Fastmcp

mcp = Fastmcp("minimal-mcp-server")

@mcp.tool()
def echo(text: str) -> str:
  """
  echo back the input text
  """
  return text

if __name__ == "__main__":
  mcp.run()