import requests
import json
import time
import os

class DeepSeekSummarizer:
    """DeepSeek API总结类"""
    
    def __init__(self, api_key, prompts_dir="prompts"):
        """
        初始化DeepSeek总结器
        
        Args:
            api_key (str): DeepSeek API密钥
            prompts_dir (str): 提示词模板目录，默认为"prompts"
        """
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.prompts_dir = prompts_dir
    
    def load_prompt_template(self, template_name):
        """
        从文件加载提示词模板
        
        Args:
            template_name (str): 模板文件名，不含扩展名
            
        Returns:
            str: 模板内容
        """
        template_path = os.path.join(self.prompts_dir, f"{template_name}.txt")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"提示词模板文件不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def create_prompt(self, text, audio_title="音频内容", template_name="audio_content_analysis"):
        """
        创建用于总结的提示词
        
        Args:
            text (str): 需要总结的文本
            audio_title (str): 音频标题
            template_name (str): 使用的模板名称
            
        Returns:
            str: 完整的提示词
        """
        template = self.load_prompt_template(template_name)
        prompt = template.format(
            audio_title=audio_title,
            content=text
        )
        return prompt
    
    def summarize(self, text, audio_title="音频内容", template_name="audio_content_analysis"):
        """
        使用DeepSeek API进行内容总结
        
        Args:
            text (str): 需要总结的文本
            audio_title (str): 音频标题
            template_name (str): 使用的模板名称
            
        Returns:
            str: 总结结果
        """
        prompt = self.create_prompt(text, audio_title, template_name)
        
        payload = json.dumps({
            "messages": [
                {
                    "content": prompt,
                    "role": "user"
                }
            ],
            "model": "deepseek-chat",
            "frequency_penalty": 0,
            "max_tokens": 4096,
            "presence_penalty": 0,
            "response_format": {
                "type": "text"
            },
            "stop": None,
            "stream": False,
            "stream_options": None,
            "temperature": 1,
            "top_p": 1,
            "tools": None,
            "tool_choice": "none",
            "logprobs": False,
            "top_logprobs": None
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        print("正在调用DeepSeek API进行内容总结...")
        start_time = time.time()
        
        try:
            response = requests.post(self.api_url, headers=headers, data=payload)
            response.raise_for_status()
            
            print(f"API调用耗时: {time.time() - start_time:.2f}秒")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {e}")
            return f"总结生成失败: {str(e)}"