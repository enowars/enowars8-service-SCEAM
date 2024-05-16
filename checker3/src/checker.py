from logging import LoggerAdapter
from enochecker3.utils import FlagSearcher, assert_equals, assert_in
from enochecker3 import (
    ChainDB,
    Enochecker,
    GetflagCheckerTaskMessage,
    MumbleException,
    PutflagCheckerTaskMessage,
)
import secrets
from typing import Optional
from utils import InteractionManager
import qr_codes

SERVICE_PORT = 8008
# from httpx import AsyncClient


# 0: email
# 1: export

checker = Enochecker("enoft", 8008)
def app(): return checker.app


@checker.putflag(0)
async def putflag_test(
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
async def getflag_test(
    task: PutflagCheckerTaskMessage,
    db: ChainDB,
    logger: LoggerAdapter
) -> None:

    credentials = await db.get("credentials")
    address = "http://" + task.address + ":" + str(SERVICE_PORT) + "/"
    m = InteractionManager(address, logger, credentials)
    await m.login()
    imgs = await m.download_profile_images()
    logger.info(f"Downloaded {len(imgs)} images")
    imgs = [qr_codes.read_qr_code(img) for img in imgs]
    logger.info(f"Decoded images: {imgs}")
    assert_in(task.flag, imgs, "Flag not found in images")


if __name__ == "__main__":
    checker.run()
