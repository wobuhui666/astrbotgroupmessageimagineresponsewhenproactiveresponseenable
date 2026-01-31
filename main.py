from astrbot.api.all import *
from astrbot.api.provider import ProviderRequest

class GroupImageEnabler(Star):
    """群聊图片回复启用器"""
    
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context, config)
    
    # 注意这里：必须使用 @filter.on_llm_request()
    # 且函数必须在 class 内部
    @filter.on_llm_request()
    async def handle_group_image_request(self, event: AstrMessageEvent, req: ProviderRequest):
        """处理群聊纯图片请求"""
        
        # 1. 检查是否是群聊消息
        if not event.get_group_id():
            return

        # 2. 检查 Prompt 是否为空（即没有文字）
        if not req.prompt:
            # 3. 检查是否包含图片
            if req.image_urls and len(req.image_urls) > 0:
                # 4. 修改 Prompt，添加占位符，强制触发 LLM 识图
                req.prompt = "请分析这张图片。" 
                
                # 打印日志方便调试
                self.context.logger.info(f"群聊 {event.get_group_id()} 收到纯图片，已添加占位符触发回复。")

    async def initialize(self):
        self.context.logger.info("群聊图片插件已加载")
    
    async def terminate(self):
        self.context.logger.info("群聊图片插件已卸载")
