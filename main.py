from astrbot.api.all import *
from astrbot.api.provider import ProviderRequest

class GroupImageEnabler(Star):
    """群聊图片回复启用器"""
    
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context, config)
    
    # 1. Move the function INSIDE the class
    # 2. Use the correct decorator @filter.on_llm_request()
    @filter.on_llm_request()
    async def handle_group_image_request(self, event: AstrMessageEvent, req: ProviderRequest):
        """处理群聊纯图片请求，添加占位符触发回复"""
        
        # 检查是否是群聊且没有文本内容
        if event.get_group_id() and not req.prompt:
            # 检查是否有图片内容
            if req.image_urls and len(req.image_urls) > 0:
                # 为群聊纯图片添加占位符
                req.prompt = "<attachment>"
                # Log using self.context.logger or the global logger if imported
                self.context.logger.info(f"为群聊 {event.get_group_id()} 的纯图片添加占位符")

    async def initialize(self):
        """插件初始化时调用"""
        self.context.logger.info("群聊图片回复启用器已加载")
    
    async def terminate(self):
        """插件卸载时调用"""
        self.context.logger.info("群聊图片回复启用器已卸载")
