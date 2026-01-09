import os

os.environ["GENIE_DATA_DIR"] = r"GenieData"
from genie_tts.Server import TTSPayload
import genie_tts as genie

import asyncio
from typing import Optional, Callable, Union, AsyncIterator
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from genie_tts.Audio.ReferenceAudio import ReferenceAudio
from genie_tts.Core.TTSPlayer import tts_player
from genie_tts.Utils.Shared import context
from genie_tts.Internal import _reference_audios
import struct

logger = logging.getLogger(__name__)

app = FastAPI()


def run_tts_in_background(
  character_name: str,
  text: str,
  split_sentence: bool,
  save_path: Optional[str],
  chunk_callback: Callable[[Optional[bytes]], None]
):
  try:
    context.current_speaker = character_name
    context.current_prompt_audio = ReferenceAudio(
      prompt_wav=_reference_audios[character_name]['audio_path'],
      prompt_text=_reference_audios[character_name]['audio_text'],
      language=_reference_audios[character_name]['language'],
    )
    tts_player.start_session(
      play=False,
      split=split_sentence,
      save_path=save_path,
      chunk_callback=chunk_callback,
    )
    tts_player.feed(text)
    tts_player.end_session()
    tts_player.wait_for_tts_completion()
  except Exception as e:
    logger.error(f"Error in TTS background task: {e}", exc_info=True)

import lameenc


async def audio_stream_generator(queue: asyncio.Queue) -> AsyncIterator[bytes]:
  # 1. 初始化 MP3 编码器
  # 参数：采样率 32000, 单声道, 质量(2=高), 码率(128kbps)
  encoder = lameenc.Encoder()
  encoder.set_bit_rate(128)
  encoder.set_in_sample_rate(32000)
  encoder.set_channels(1)
  encoder.set_quality(2)

  while True:
    chunk = await queue.get()

    if chunk is None:
      # 2. 结束流时，刷出编码器剩余的数据
      final_mp3_data = encoder.flush()
      if final_mp3_data:
        yield bytes(final_mp3_data)
      break

    # 3. 实时编码 PCM 块为 MP3 块
    # 注意：TTSPlayer 传出来的是 int16 的 bytes，lameenc 直接支持
    mp3_data = encoder.encode(chunk)
    if mp3_data:
      yield bytes(mp3_data)


@app.post("/tts")
async def tts_endpoint(payload: TTSPayload):
  loop = asyncio.get_running_loop()
  stream_queue: asyncio.Queue[Union[bytes, None]] = asyncio.Queue()

  def tts_chunk_callback(chunk: Optional[bytes]):
    loop.call_soon_threadsafe(stream_queue.put_nowait, chunk)

  loop.run_in_executor(
    None,
    run_tts_in_background,
    payload.character_name,
    payload.text,
    payload.split_sentence,
    payload.save_path,
    tts_chunk_callback
  )

  return StreamingResponse(audio_stream_generator(stream_queue), media_type="audio/mpeg")


def start_server(host: str = "127.0.0.1", port: int = 8000, workers: int = 1):
  genie.load_predefined_character('feibi')
  genie.load_predefined_character('mika')
  genie.load_predefined_character('thirtyseven')
  uvicorn.run(app, host=host, port=port, workers=workers)


if __name__ == "__main__":
  start_server(host="0.0.0.0", port=8000, workers=1)
