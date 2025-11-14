import google.generativeai as genai
from config import config
import json
import random
import re

class GeminiService:
    def __init__(self):
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.model = None
    
    async def analyze_message(self, message_text: str) -> dict:
        if not self.model or not config.ENABLE_AI_FILTER:
            return {"is_spam": False, "reason": "AI filter disabled"}
        
        prompt = f"""
分析以下消息，判断是否包含垃圾信息或恶意内容: {message_text}
请以JSON格式回复: {{"is_spam": true/false, "reason": "原因"}}
"""
        try:
            response = await self.model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini分析失败: {e}")
            return {"is_spam": False, "reason": "分析失败"}
    
    async def generate_unblock_question(self) -> dict:
        if not self.model:
            return {
                "question": "中国的首都是哪里？",
                "answer": "北京"
            }
        
        prompt = """
生成一个简单的常识问题用于解封验证。
请以JSON格式回复: {{"question": "问题", "answer": "答案"}}
"""
        try:
            response = await self.model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"生成问题失败: {e}")
            return {
                "question": "中国的首都是哪里？",
                "answer": "北京"
            }

    async def generate_verification_challenge(self) -> dict:
        if not self.model:
            return {
                "question": "1 + 1 = ?",
                "correct_answer": "2",
                "options": ["1", "2", "3", "4"]
            }

        prompt = """
请生成一个用于人机验证的常识性问题。
要求：
1. 问题应该简单，大部分人都能回答。
2. 提供一个正确答案和三个看起来合理但错误的干扰项。
3. 所有内容必须为简体中文。
4. 以JSON格式返回，包含以下键： "question", "correct_answer", "incorrect_answers" (一个包含三个字符串的列表)。

示例:
{
  "question": "太阳从哪个方向升起？",
  "correct_answer": "东方",
  "incorrect_answers": ["西方", "南方", "北方"]
}
"""
        try:
            response = await self.model.generate_content_async(prompt)
            
            if not response.text:
                raise ValueError("Gemini API返回空响应")

            
            clean_text = re.sub(r'```json\s*|\s*```', '', response.text).strip()
            data = json.loads(clean_text)
            
            
            correct_answer = data['correct_answer']
            options = data['incorrect_answers'] + [correct_answer]
            random.shuffle(options)
            
            return {
                "question": data['question'],
                "correct_answer": correct_answer,
                "options": options
            }
        except Exception as e:
            print(f"生成验证问题失败: {e}")
            
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Gemini原始响应: {response.text}")
            
            return {
                "question": "1 + 1 = ?",
                "correct_answer": "2",
                "options": ["1", "2", "3", "4"]
            }

gemini_service = GeminiService()