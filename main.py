from astrbot.api.all import *
from astrbot.api.provider import ProviderRequest  # <--- This fixes the specific error you are seeing

class GroupImageEnabler(Star):
    """群聊图片回复启用器"""
    
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context, config)
    
    # We place the handler INSIDE the class.
    # @filter.on_llm_request() registers the hook automatically.
    @filter.on_llm_request()
    async def handle_group_image_request(self, event: AstrMessageEvent, req: ProviderRequest):
        """处理群聊纯图片请求，添加占位符触发回复"""
        
        # Check if it's a group chat and the text prompt is empty
        if event.get_group_id() and not req.prompt:
            # Check if the request contains image URLs
            if req.image_urls and len(req.image_urls) > 0:
                # Add a placeholder text to trigger the LLM to see the image
                req.prompt = "<attachment>"
                self.context.logger.info(f"Group {event.get_group_id()}: Added placeholder for image-only message.")

    async def initialize(self):
        """Called when plugin loads"""
        self.context.logger.info("Group Image Enabler loaded successfully.")
    
    async def terminate(self):
        """Called when plugin unloads"""
        self.context.logger.info("Group Image Enabler unloaded.")
