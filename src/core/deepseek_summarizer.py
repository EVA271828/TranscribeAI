import requests
import json
import time
import os
import threading
import uuid

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
        self._lock = threading.Lock()
        # 用于停止标志的全局控制 - 使用uuid作为键，列表存储实际标志
        self._stop_flags = {}  # {uuid: [False]}

    def stop(self):
        """设置停止标志，用于中断所有长时间运行的总结"""
        with self._lock:
            for flag in self._stop_flags.values():
                flag[0] = True
        print("收到停止信号，正在中断所有总结...")

    def reset_stop_flags(self):
        """重置所有停止标志"""
        with self._lock:
            self._stop_flags.clear()

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

    def _summarize_worker(self, text, audio_title, template_name, stop_flag_id, result_container):
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

            # 使用合理的超时时间并增加重试机制
            max_retries = 3
            retry_count = 0
            timeout = 120  # 初始超时时间设为120秒

            while retry_count < max_retries:
                # 检查停止标志
                with self._lock:
                    stop_flag = self._stop_flags.get(stop_flag_id, [False])
                    should_stop = stop_flag[0]

                if should_stop:
                    print("总结被用户中断")
                    result_container['result'] = ""
                    return

                try:
                    response = requests.post(self.api_url, headers=headers, data=payload, timeout=timeout)
                    response.raise_for_status()

                    # 检查是否在请求过程中被中断
                    with self._lock:
                        stop_flag = self._stop_flags.get(stop_flag_id, [False])
                        should_stop = stop_flag[0]

                    if should_stop:
                        print("总结被用户中断")
                        result_container['result'] = ""
                        return

                    print(f"API调用耗时: {time.time() - start_time:.2f}秒")

                    result = response.json()
                    result_container['result'] = result["choices"][0]["message"]["content"]
                    return

                except requests.exceptions.Timeout:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"API调用超时，正在重试 ({retry_count}/{max_retries})...")
                        # 检查停止标志
                        with self._lock:
                            stop_flag = self._stop_flags.get(stop_flag_id, [False])
                            should_stop = stop_flag[0]

                        if should_stop:
                            print("总结被用户中断")
                            result_container['result'] = ""
                            return
                        # 增加超时时间后重试
                        timeout = 180
                        continue
                    else:
                        print(f"API调用超时，已重试{max_retries}次，放弃")
                        result_container['error'] = "总结生成失败: API调用超时，请检查网络连接或稍后重试"
                        return

                except requests.exceptions.RequestException as e:
                    retry_count += 1
                    if retry_count < max_retries and isinstance(e, requests.exceptions.ConnectionError):
                        print(f"API调用网络错误，正在重试 ({retry_count}/{max_retries})...")
                        # 检查停止标志
                        with self._lock:
                            stop_flag = self._stop_flags.get(stop_flag_id, [False])
                            should_stop = stop_flag[0]

                        if should_stop:
                            print("总结被用户中断")
                            result_container['result'] = ""
                            return
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    else:
                        print(f"API调用失败: {e}")
                        result_container['error'] = f"总结生成失败: {str(e)}"
                        return

        except Exception as e:
            print(f"总结过程中出错: {e}")
            result_container['error'] = str(e)
        finally:
            # 清理停止标志
            with self._lock:
                if stop_flag_id in self._stop_flags:
                    del self._stop_flags[stop_flag_id]

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
        # 为此总结任务创建独立的停止标志ID和结果容器
        stop_flag_id = uuid.uuid4()
        result_container = {'result': None, 'error': None}

        # 注册停止标志
        with self._lock:
            self._stop_flags[stop_flag_id] = [False]

        # 创建并启动总结线程
        summarize_thread = threading.Thread(
            target=self._summarize_worker,
            args=(text, audio_title, template_name, stop_flag_id, result_container),
            daemon=True
        )
        summarize_thread.start()

        # 等待线程完成（使用轮询方式，可以被 stop() 中断）
        while True:
            if not summarize_thread.is_alive():
                break
            # 检查停止标志
            with self._lock:
                should_stop = self._stop_flags.get(stop_flag_id, [False])[0]
            if should_stop:
                return ""
            time.sleep(0.1)

        # 返回结果或抛出异常
        if result_container['error']:
            return result_container['error']
        return result_container['result'] or ""
