import os
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

class AuthMiddleware(BaseMiddleware):
    def __init__(self, allowed_ids: list[int]):
        self.allowed_ids = allowed_ids
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]  # ← ИСПРАВЛЕНО: добавлено имя "data"
    ) -> Any:
        user_id = getattr(event, "from_user", None) and event.from_user.id
        if user_id not in self.allowed_ids:
            if isinstance(event, Message):
                await event.answer("Access denied")
            elif isinstance(event, CallbackQuery):
                await event.answer("Access denied")
            return
        return await handler(event, data)