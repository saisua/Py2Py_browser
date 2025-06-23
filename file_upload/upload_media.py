import asyncio
import logging
from math import ceil

from config import media_split_size, DEBUG_DISABLE_UPLOAD_MEDIA_DATA

from browser.utils.hash_req_res import hash_req_res

from files.utils.read_bytes import _read_bytes
from files.store_to_disk import store_to_disk


MEDIA_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Video Loader</title>
</head>
<body>
    <video id="my-p2p-video" controls autoplay/>
    <script defer>
        const video = document.getElementById('my-p2p-video');
        const mediaSource = new MediaSource();
        let sourceBuffer;
        let partNumber = 0;

        // Create object URL for the MediaSource
        video.src = URL.createObjectURL(mediaSource);

        mediaSource.addEventListener('sourceopen', () => {{
            // Initialize source buffer (adjust codecs to match your video)
            sourceBuffer = mediaSource.addSourceBuffer(
                {buffer_string}
            );

            // Load first part
            loadVideoPart(partNumber);
        }});

        async function loadVideoPart(partNumber) {{
            try {{
                const response = await fetch(
                    `http://stream.{media_path}.p2p/${{partNumber}}/`
                );
                const buffer = await response.arrayBuffer();

                sourceBuffer.addEventListener('updateend', () => {{
                    // When current part is loaded, queue next part
                    if (
                        !sourceBuffer.updating
                        && mediaSource.readyState === 'open'
                    ) {{
                        partNumber++;
                        loadVideoPart(partNumber);
                    }}
                }}, {{ once: true }});

                if (!sourceBuffer.updating) {{
                    sourceBuffer.appendBuffer(buffer);
                }}
            }} catch (error) {{
                console.error('Error loading video part:', error);
            }}
        }}
        </script>
</body>
</html>
"""


def gen_buffer_string(ext: str) -> str:
    """Generate proper MediaSource buffer string for given video extension.

    Args:
        ext: Video file extension (without dot)

    Returns:
        Proper MIME type and codecs string for MediaSource

    Raises:
        ValueError: If extension is not supported
    """
    codec_map = {
        "mp4": "video/mp4; codecs='avc1.42E01E, mp4a.40.2'",
        "webm": "video/webm; codecs='vp9, opus'",
        "mkv": "video/x-matroska; codecs='avc1.42E01E, mp4a.40.2'",
        "avi": "video/x-msvideo; codecs='avc1.42E01E, mp4a.40.2'",
        "mov": "video/quicktime; codecs='avc1.42E01E, mp4a.40.2'",
        "wmv": "video/x-ms-wmv; codecs='wvc1'",
        "flv": "video/x-flv; codecs='avc1.42E01E, mp4a.40.2'",
        "ogg": "video/ogg; codecs='theora, vorbis'",
        "m4a": "audio/mp4; codecs='mp4a.40.2'",
        "aac": "audio/mp4; codecs='mp4a.40.2'",
        "flac": "audio/flac",
        "wma": "audio/x-ms-wma"
    }

    try:
        return codec_map[ext.lower()]
    except KeyError:
        raise ValueError(f"Unsupported video extension: {ext}")


async def upload_media(session_maker, media_path: str):
    ext = media_path.rsplit(".", 1)[-1]
    html_url = f"http://{media_path}.p2p"
    html_url_hash, domain_hash = hash_req_res(
        f"{html_url}/",
        "local",
        "GET",
    )

    logging.info(f"uploading media {html_url}/ {html_url_hash}")

    if not DEBUG_DISABLE_UPLOAD_MEDIA_DATA:
        media_data = await _read_bytes(media_path, decompress=False)
        num_parts: int = ceil(
            len(media_data) / media_split_size
        )

        part_coros = list()
        for i in range(num_parts):
            print("storing part", i, "of", num_parts - 1, flush=False)
            part_data = media_data[
                i * media_split_size:(i + 1) * media_split_size
            ]

            part_url = f"http://stream.{media_path}.p2p/{i}"

            part_url_hash, domain_hash = hash_req_res(
                f"{part_url}/",
                "local",
                "GET",
            )
            logging.info(f"uploading part {part_url} {part_url_hash}")

            part_coros.append(
                store_to_disk(
                    session_maker,
                    part_url_hash,
                    domain_hash,
                    part_data,
                )
            )

            if len(part_coros) == 50:
                await asyncio.gather(*part_coros)
                part_coros.clear()

        if part_coros:
            await asyncio.gather(*part_coros)

    url_hash, domain_hash = hash_req_res(
        f"{html_url}/",
        "local",
        "GET",
    )
    logging.info(f"uploading media html {html_url} {url_hash}")

    await store_to_disk(
        session_maker,
        html_url_hash,
        domain_hash,
        bytes(
            MEDIA_HTML_TEMPLATE.format(
                media_path=media_path,
                buffer_string=gen_buffer_string(ext),
            ),
            "utf-8",
        ),
    )
