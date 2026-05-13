import logging
import os
import sys

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
from bot.vk_handler import handle_message

os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def _build_session() -> tuple[vk_api.VkApi, object]:
    session = vk_api.VkApi(token=config.VK_TOKEN)
    return session, session.get_api()


def main() -> None:
    py_version = ".".join(str(v) for v in sys.version_info[:3])
    logger.info(
        "Запуск бота '%s' | Python %s | group_id=%s",
        config.BOT_NAME, py_version, config.VK_GROUP_ID,
    )
    print(f"[{config.BOT_NAME}] Запуск... Python {py_version}, group_id={config.VK_GROUP_ID}")

    try:
        session, vk = _build_session()
        longpoll = VkBotLongPoll(session, config.VK_GROUP_ID)
    except Exception as e:
        logger.exception("Ошибка подключения к VK")
        print(f"Ошибка подключения к VK: {e}", file=sys.stderr)
        sys.exit(1)

    logger.info("Bot Long Poll запущен, ожидание событий")
    print(f"[{config.BOT_NAME}] Бот запущен. Нажми Ctrl+C для остановки.")

    try:
        for event in longpoll.listen():
            logger.debug("Событие: %s", event.type)
            print(f"Событие: {event.type}")
            if event.type == VkBotEventType.MESSAGE_NEW:
                handle_message(vk, event)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (KeyboardInterrupt)")
        print(f"\n[{config.BOT_NAME}] Остановлен.")
    except Exception:
        logger.exception("Критическая ошибка в Long Poll loop")
        print("Критическая ошибка. Подробности в logs/bot.log", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
