import asyncio
import aiohttp
import json

async def test_stream_query(question: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/api/v1/knowledge/query',
            json={'question': question, 'stream': True}
        ) as response:
            async for line in response.content:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    if data['type'] == 'thinking':
                        print('\n思考中:', data['content'])
                    elif data['type'] == 'source':
                        print(f'\n参考来源 {data["index"]}:', data['content'])
                    elif data['type'] == 'content':
                        print(data['content'], end='', flush=True)
                    elif data['type'] == 'done':
                        print('\n\n回答完成')
                    elif data['type'] == 'error':
                        print('\n错误:', data['content'])

if __name__ == '__main__':
    question = "如何提高ODEX优化进度?"
    asyncio.run(test_stream_query(question)) 