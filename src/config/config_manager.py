import configparser
import os

class ConfigManager:
    """配置管理器，负责读取和管理API密钥等配置信息"""
    
    def __init__(self, config_file=None):
        """
        初始化配置管理器
        
        Args:
            config_file (str): 配置文件路径，默认为'src/config/config.ini'
        """
        if config_file is None:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_file = os.path.join(project_root, 'src', 'config', 'config.ini')
        
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # 如果配置文件不存在，创建默认配置
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        self.config['api'] = {
            'api_key': 'YOUR_DEEPSEEK_API_KEY_HERE'
        }
        self.config['settings'] = {
            'default_model': 'small',
            'default_template': 'audio_content_analysis',
            'output_folder': 'output'
        }
        self.save_config()
    
    def get_api_key(self):
        """
        获取API密钥
        
        Returns:
            str: API密钥，如果未设置则返回None
        """
        api_key = self.config.get('api', 'api_key')
        if api_key == 'YOUR_DEEPSEEK_API_KEY_HERE':
            return None
        return api_key
    
    def set_api_key(self, api_key):
        """
        设置API密钥
        
        Args:
            api_key (str): API密钥
        """
        self.config.set('api', 'api_key', api_key)
        self.save_config()
    
    def get_default_model(self):
        """
        获取默认模型
        
        Returns:
            str: 默认模型名称
        """
        return self.config.get('settings', 'default_model')
    
    def set_default_model(self, model):
        """
        设置默认模型
        
        Args:
            model (str): 模型名称
        """
        self.config.set('settings', 'default_model', model)
        self.save_config()
    
    def get_default_template(self):
        """
        获取默认模板
        
        Returns:
            str: 默认模板名称
        """
        return self.config.get('settings', 'default_template')
    
    def set_default_template(self, template):
        """
        设置默认模板
        
        Args:
            template (str): 模板名称
        """
        self.config.set('settings', 'default_template', template)
        self.save_config()
    
    def get_output_folder(self):
        """
        获取输出文件夹
        
        Returns:
            str: 输出文件夹路径
        """
        try:
            return self.config.get('settings', 'output_folder')
        except (configparser.NoOptionError, configparser.NoSectionError):
            # 如果配置文件中没有output_folder选项，则返回默认值
            return 'output'
    
    def set_output_folder(self, folder):
        """
        设置输出文件夹
        
        Args:
            folder (str): 输出文件夹路径
        """
        self.config.set('settings', 'output_folder', folder)
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)