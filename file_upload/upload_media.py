import asyncio
import logging
from pathlib import Path
from math import ceil

from config import (
	logger,
	media_split_size,
	DEBUG_DISABLE_UPLOAD_MEDIA_DATA,
)

from browser.utils.hash_req_res import hash_req_res

from files.utils.read_bytes import _read_bytes
from files.store_to_disk import store_to_disk

from file_upload.utils.format_file import format_file_to_dump


MEDIA_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Media Loader</title>
</head>
<body>
    <{media_type} id="my-p2p-{media_type}" controls></{media_type}>
    <script defer>
        const media = document.getElementById('my-p2p-{media_type}');
        const mimeCodec = `{buffer_string}`;
        const BUFFER_THRESHOLD = 30; // seconds
        const BUFFER_WAIT_TIME = 7000; // milliseconds

        if (
            "MediaSource" in window &&
            MediaSource.isTypeSupported(mimeCodec)
        ) {{
            const mediaSource = new MediaSource();
            let sourceBuffer;
            let partNumber = 0;
            let isBuffering = false;

            mediaSource.addEventListener('sourceopen', () => {{
                sourceBuffer = mediaSource.addSourceBuffer(mimeCodec);
                checkBuffer();
            }});

            media.src = URL.createObjectURL(mediaSource);

            function checkBuffer() {{
                const buffer_size = (
                    media.buffered.length > 0 ?
                    sourceBuffer.buffered.end(
                        media.buffered.length - 1
                    ) - media.currentTime :
                    0
                );
                // console.log("buffer_size", buffer_size);
                if (
                    buffer_size < BUFFER_THRESHOLD &&
                    !isBuffering
                ) {{
                    isBuffering = true;
                    loadMediaPart(partNumber);
                    partNumber++;
                }} else {{
                    // console.log("waiting 10s to buffer");
                    setTimeout(() => {{
                        isBuffering = false;
                        checkBuffer();
                    }}, BUFFER_WAIT_TIME);
                }}
            }}

            async function loadMediaPart(partNumber) {{
                try {{
                    const response = await fetch(
                        `http://stream.{media_domain}/${{partNumber}}/`
                    );
                    const buffer = await response.arrayBuffer();

                    sourceBuffer.addEventListener('updateend', () => {{
                        if (
                            !sourceBuffer.updating &&
                            mediaSource.readyState === 'open'
                        ) {{
                            isBuffering = false;
                            checkBuffer();
                        }} else {{
                            // console.log("waiting 10s to buffer");
                            setTimeout(() => {{
                                isBuffering = false;
                                checkBuffer();
                            }}, BUFFER_WAIT_TIME);
                        }}
                    }}, {{ once: true }});

                    if (!sourceBuffer.updating) {{
                        sourceBuffer.appendBuffer(buffer);
                    }}
                }} catch (error) {{
                    console.error('Error loading media part:', error);
                    mediaSource.endOfStream();
                }}
            }}
        }} else {{
            console.error("Unsupported MIME type or codec: ", mimeCodec);
        }}
    </script>
</body>
</html>
"""


def gen_media_type(ext: str) -> str:
    """Generate proper MediaSource buffer string for given video extension.

    Args:
        ext: Video file extension (without dot)

    Returns:
        Proper MIME type and codecs string for MediaSource

    Raises:
        ValueError: If extension is not supported
    """
    codec_map = {
        # "mp4": "video/mp4",
        "webm": "video/webm",
        # "mkv": "video/x-matroska",
        # "avi": "video/x-msvideo",
        # "mov": "video/quicktime",
        # "wmv": "video/x-ms-wmv",
        # "flv": "video/x-flv",
        # "ogg": "video/ogg",
        "m4a": "audio/mp4",
        "aac": "audio/mp4",
        "weba": "audio/webm",
        # "flac": "audio/flac",
        # "wma": "audio/x-ms-wma"
    }

    try:
        return codec_map[ext.lower()]
    except KeyError:
        raise ValueError(f"Unsupported video extension: {ext}")


async def upload_media(session_maker, media_path: str):
    file_name = format_file_to_dump(Path(media_path).name.rstrip('/'))
    ext = file_name.rsplit(".", 1)[-1]
    html_domain = f"{file_name}.p2p"
    html_url = f"http://{html_domain}"
    html_url_hash, domain_hash = hash_req_res(
        f"{html_url}/",
        html_domain,
        "GET",
    )

    if logger.isEnabledFor(logging.INFO):
        logger.info(f"uploading media {html_url}/ {html_url_hash}")

    if not DEBUG_DISABLE_UPLOAD_MEDIA_DATA:
        media_data = await _read_bytes(media_path, decompress=False)
        num_parts: int = ceil(
            len(media_data) / media_split_size
        )

        part_domain = f"stream.{html_domain}"

        part_coros = list()
        for i in range(num_parts):
            if logger.isEnabledFor(logging.INFO):
                logger.info(
                    f"storing part {i} of {num_parts - 1}"
                )
            part_data = media_data[
                i * media_split_size:(i + 1) * media_split_size
            ]

            part_url = f"http://{part_domain}/{i}"

            part_url_hash, domain_hash = hash_req_res(
                f"{part_url}/",
                part_domain,
                "GET",
            )
            if logger.isEnabledFor(logging.INFO):
                logger.info(f"uploading part {part_url} {part_url_hash}")

            part_coros.append(
                store_to_disk(
                    session_maker,
                    part_url_hash,
                    domain_hash,
                    part_data,
                )
            )

            if len(part_coros) == 10:
                await asyncio.gather(*part_coros)
                part_coros.clear()

        if part_coros:
            await asyncio.gather(*part_coros)

    url_hash, domain_hash = hash_req_res(
        f"{html_url}/",
        html_domain,
        "GET",
    )
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Url: {html_url}, "
                     f"Domain: {html_domain} "
                     f"-> {url_hash}")
    if logger.isEnabledFor(logging.INFO):
        logger.info(f"uploading media html {html_url} {url_hash}")

    buffer_string = gen_media_type(ext)
    media_type = buffer_string.split("/", 1)[0]

    await store_to_disk(
        session_maker,
        html_url_hash,
        domain_hash,
        bytes(
            MEDIA_HTML_TEMPLATE.format(
                media_domain=html_domain,
                buffer_string=buffer_string,
                media_type=media_type,
            ),
            "utf-8",
        ),
    )
