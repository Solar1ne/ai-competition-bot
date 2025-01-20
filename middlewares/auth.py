from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from handlers.start import RegistrationState, is_user_registered

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Проверка регистрации
        try:
            if not isinstance(event, Message):
                return await handler(event, data)
            
            # Получаем текущее состояние FSM
            state: FSMContext = data.get("state")
            if state:
                current_state = await state.get_state()
                # Пропускаем сообщения во время процесса регистрации
                if current_state in [RegistrationState.NAME.state, RegistrationState.EMAIL.state]:
                    return await handler(event, data)
            
            # Используем общую функцию проверки регистрации
            is_registered, _ = is_user_registered(event.from_user.id)
            if not is_registered and event.text not in ["/start", "/register", "/help"]:
                await event.answer("Сначала зарегистрируйтесь: /register")
                return
                
        except Exception as e:
            print(f"Error in auth middleware: {e}")
            if event.text not in ["/start", "/register", "/help"]:
                await event.answer("Сначала зарегистрируйтесь: /register")
                return
            
        return await handler(event, data)