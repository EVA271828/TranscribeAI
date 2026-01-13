import requests
import json
import time
import os
import threading

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
        self._stop_flag = False
        self._summarize_thread = None
        self._summarize_result = None
        self._summarize_error = None
        self._lock = threading.Lock()

    def stop(self):
        """设置停止标志，用于中断长时间运行的总结"""
        self._stop_flag = True
        # 等待总结线程结束（短超时）
        with self._lock:
            if self._summarize_thread and self._summarize_thread.is_alive():
                self._summarize_thread.join(timeout=2)
        print("收到停止信号，正在中断总结...")

    def reset_stop_flag(self):
        """重置停止标志"""
        self._stop_flag = False
        with self._lock:
            self._summarize_thread = None
            self._summarize_result = None
            self._summarize_error = None

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

    def _summarize_worker(self, text, audio_title, template_name):
        """总结工作线程，用于在后台执行总结以便快速停止"""
        try:
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

            # 使用较短的超时时间，使得可以快速响应停止信号
            # 如果API调用超过5秒还未完成，检查停止标志
            timeout = 5  # 短超时
            while True:
                # 检查停止标志
                if self._stop_flag:
                    print("总结被用户中断")
                    self._summarize_result = ""
                    return

                try:
                    response = requests.post(self.api_url, headers=headers, data=payload, timeout=timeout)
                    response.raise_for_status()

                    # 检查是否在请求过程中被中断
                    if self._stop_flag:
                        print("总结被用户中断")
                        self._summarize_result = ""
                        return

                    print(f"API调用耗时: {time.time() - start_time:.2f}秒")

                    result = response.json()
                    self._summarize_result = result["choices"][0]["message"]["content"]
                    return

                except requests.exceptions.Timeout:
                    # 超时后检查停止标志
                    if self._stop_flag:
                        print("总结被用户中断")
                        self._summarize_result = ""
                        return
                    # 如果没有停止标志，增加超时时间继续尝试
                    timeout = 60
                except requests.exceptions.RequestException as e:
                    print(f"API调用失败: {e}")
                    self._summarize_error = f"总结生成失败: {str(e)}"
                    return

        except Exception as e:
            print(f"总结过程中出错: {e}")
            self._summarize_error = str(e)

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
        # 重置结果和错误
        with self._lock:
            self._summarize_result = None
            self._summarize_error = None
            self._stop_flag = False

        # 创建并启动总结线程
        with self._lock:
            self._summarize_thread = threading.Thread(
                target=self._summarize_worker,
                args=(text, audio_title, template_name),
                daemon=True
            )
            self._summarize_thread.start()

        # 等待线程完成（使用轮询方式，可以被 stop() 中断）
        while True:
            with self._lock:
                if not self._summarize_thread.is_alive():
                    break
                if self._stop_flag:
                    return ""
            time.sleep(0.1)

        # 返回结果或抛出异常
        with self._lock:
            if self._summarize_error:
                return self._summarize_error
            return self._summarize_result or ""
