import logging
import time

import httpx
import coloredlogs

logger = logging.getLogger("MassiveRidiSelect")
coloredlogs.install(level="INFO")

if __name__ == "__main__":
    cookie = input("Cookie:")
    header = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    logger.info("Get Information From Cookie...")
    information = httpx.get(
        "https://account.ridibooks.com/accounts/me",
        headers=header).json()
    if information == {"message": "Unauthorized"}:
        logger.error("Cookie is Invalid")
        exit(255)
    logger.info(f"User Email : {information['result']['email']}")
    logger.info("Get Information From Cookie... Done")
    logger.info("loading first page of select...")
    select_first_page = httpx.get(
        "https://select-api.ridibooks.com/api/pages/collections/recent?page=1",
        headers=header
    ).json()
    logger.info(f"last page : {select_first_page['total_page']}")
    logger.info(f"total book count : {select_first_page['total_count']}")
    logger.info("start adding books...")
    for index in range(1, select_first_page['total_page']):
        logger.info(f"loading page {index}...")
        page = httpx.get(
            f"https://select-api.ridibooks.com/api/pages/collections/recent?page={index}",
            headers=header
        ).json()
        for book in page["books"]:
            logger.info(f"Adding book {book['id']}-{book['title']['main']}")
            try:
                httpx.post(
                    "https://ridibooks.com/api/select/users/me/books",
                    headers=header,
                    json={
                        "b_id": book["id"],
                    },
                    timeout=5
                )
                r = httpx.get(
                    f"https://ridibooks.com/api/select/users/me/books/{book['id']}",
                    headers=header,
                    timeout=5
                )
            except httpx.ReadTimeout:
                logger.error(f"Timeout - On https://select.ridibooks.com/book/{book['id']}")
                logger.error(f"Add Book Manually")
                continue
            if r.status_code == 401:
                logger.warning("Cookie Expired")
                logger.warning("Insert New Cookie")
                header["Cookie"] = input("Cookie : ")
                httpx.post(
                    "https://ridibooks.com/api/select/users/me/books",
                    headers=header,
                    json={
                        "b_id": book["id"],
                    }
                )
                r = httpx.get(
                    f"https://ridibooks.com/api/select/users/me/books/{book['id']}",
                    headers=header
                )
            logger.info(f"Added : {r.status_code}")
            time.sleep(0.5)
