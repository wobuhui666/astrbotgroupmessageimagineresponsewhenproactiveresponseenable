from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image, Plain

@register("image_reply", "AstrBot", "Active reply to images in group chat", "1.0.0")
class ImageReply(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        """Handle group messages to check for images and reply if active reply is enabled."""
        
        # 1. Check if the message contains an image
        has_image = False
        image_urls = []
        for component in event.message_obj.message:
            if isinstance(component, Image):
                has_image = True
                try:
                    # Convert to file path (handles URL downloading, base64, etc.)
                    # This ensures we get a valid path/URL even if the platform (like QQ) 
                    # provides it in a different format or lacks a public URL.
                    file_path = await component.convert_to_file_path()
                    image_urls.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to convert image component to file path: {e}")
        
        if not has_image:
            return

        # 2. Check if active reply is enabled in the configuration
        # Logic borrowed from astrbot/builtin_stars/astrbot/main.py
        ltmse = self.context.get_config(umo=event.unified_msg_origin).get("provider_ltm_settings", {})
        active_reply_config = ltmse.get("active_reply", {})
        
        if not active_reply_config.get("enable", False):
            return

        # 3. Check whitelist (if applicable, though active reply usually implies checking this)
        # Note: 'astrbot/builtin_stars/astrbot/long_term_memory.py' has whitelist logic.
        # We should probably respect it to be consistent.
        whitelist = active_reply_config.get("whitelist", [])
        if whitelist:
             if event.unified_msg_origin not in whitelist and \
                (event.get_group_id() and event.get_group_id() not in whitelist):
                return

            # 4. Request LLM to reply
        # We bypass the probability check as per user request (implied "always reply to images")
        
        provider = self.context.get_using_provider(event.unified_msg_origin)
        if not provider:
            logger.error("No LLM provider found. Cannot reply to image.")
            return

        try:
            # We use event.request_llm which handles the pipeline
            # Use the message string as prompt (which might be empty or caption if parsed, but LLM sees the image)
            # If the message is JUST an image, the prompt might be empty.
            
            prompt = event.message_str
            # If prompt is empty or just contains "[Image]" placeholder, give it a better prompt
            if not prompt.strip() or prompt.strip() == "[图片]":
                prompt = "This is an image sent by a user in the group chat. Please reply to it appropriately."

            # Get current conversation to ensure persona is used
            session_curr_cid = await self.context.conversation_manager.get_curr_conversation_id(
                event.unified_msg_origin,
            )
            conv = None
            if session_curr_cid:
                 conv = await self.context.conversation_manager.get_conversation(
                    event.unified_msg_origin,
                    session_curr_cid,
                )

            # Construct the request
            yield event.request_llm(
                prompt=prompt,
                func_tool_manager=self.context.get_llm_tool_manager(),
                session_id=event.session_id,
                conversation=conv,
                image_urls=image_urls
            )
            
        except Exception as e:
            logger.error(f"ImageReply plugin error: {e}")
