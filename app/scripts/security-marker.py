import asyncio, json
from pathlib import Path
from marketplace.security_marker import compare_marker

async def main():
    result = await compare_marker()
    Path('/tmp/security-marker.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
