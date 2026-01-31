from astrbot.api.all import *  
from astrbot.core.star import Star  
  
@register_on_llm_request()  
async def handle_group_image_request(event: AstrMessageEvent, req: ProviderRequest):  
    """处理群聊纯图片请求，添加占位符触发回复"""  
      
    # 检查是否是群聊且没有文本内容  
    if event.get_group_id() and not req.prompt:  
        # 检查是否有图片内容  
        if req.image_urls and len(req.image_urls) > 0:  
            # 为群聊纯图片添加占位符  
            req.prompt = "<attachment>"  
            logger.info(f"为群聊 {event.get_group_id()} 的纯图片添加占位符")  
  
class GroupImageEnabler(Star):  
    def __init__(self, context: Context, config: AstrBotConfig):  
        super().__init__(context, config)  
      
    async def initialize(self):  
        logger.info("群聊图片回复启用器已加载")
