import os
import tempfile
from typing import List, Optional

import gradio as gr
import numpy as np
import torch
from PIL import Image
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video
from torchvision.io import read_video

os.environ["TOKENIZERS_PARALLELISM"] = "false"

DEFAULT_MODEL = "linyq/kiwi-edit-5b-instruct-reference-diffusers"
MODEL_CHOICES = [
    "linyq/kiwi-edit-5b-instruct-reference-diffusers",
]

_PIPELINE_CACHE = {}


def get_device() -> str:
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def get_dtype(device: str) -> torch.dtype:
    return torch.bfloat16 if device.startswith("cuda") else torch.float32


def load_video_frames(video_path: str, max_frames: int, max_pixels: int) -> List[Image.Image]:
    frames, _, _ = read_video(video_path, pts_unit="sec")
    out = []
    for i in range(min(len(frames), max_frames)):
        img = Image.fromarray(frames[i].numpy())
        w, h = img.size
        scale = min(1.0, (max_pixels / (w * h)) ** 0.5)
        if scale < 1.0:
            new_w = max((int(w * scale) // 16) * 16, 16)
            new_h = max((int(h * scale) // 16) * 16, 16)
            img = img.resize((new_w, new_h), Image.LANCZOS)
        out.append(img)
    return out


def normalize_video_output(result):
    if isinstance(result, list):
        return result
    if hasattr(result, "frames"):
        frames = result.frames
        if isinstance(frames, list) and len(frames) > 0 and isinstance(frames[0], list):
            return frames[0]
        return frames
    if hasattr(result, "videos"):
        videos = result.videos
        if isinstance(videos, list) and len(videos) > 0:
            return videos[0]
        return videos
    if isinstance(result, torch.Tensor):
        # Expected shapes: [F, H, W, C] or [B, F, C, H, W]
        if result.ndim == 5:
            result = result[0].permute(0, 2, 3, 1)
        if result.ndim == 4:
            return [frame.detach().cpu().numpy() for frame in result]
    return result


def load_pipeline(model_id: str):
    device = get_device()
    dtype = get_dtype(device)
    key = (model_id, device, str(dtype))
    if key in _PIPELINE_CACHE:
        return _PIPELINE_CACHE[key], device

    pipe = DiffusionPipeline.from_pretrained(model_id, trust_remote_code=True)
    pipe.to(device, dtype=dtype)
    _PIPELINE_CACHE[key] = pipe
    return pipe, device


def concat_frames(left_frames: List[Image.Image], right_frames) -> List[np.ndarray]:
    if not left_frames or not right_frames:
        return []

    n = min(len(left_frames), len(right_frames))
    out = []
    for i in range(n):
        left = left_frames[i].convert("RGB")
        right = right_frames[i]
        if isinstance(right, np.ndarray):
            right_img = Image.fromarray(right.astype(np.uint8))
        else:
            right_img = right.convert("RGB")

        h = max(left.height, right_img.height)
        w = left.width + right_img.width
        canvas = Image.new("RGB", (w, h), (0, 0, 0))
        canvas.paste(left, (0, 0))
        canvas.paste(right_img, (left.width, 0))
        out.append(np.array(canvas))
    return out


def run_edit(
    source_video: str,
    prompt: str,
    ref_image: Optional[str],
    model_id: str,
    max_frames: int,
    max_pixels: int,
    steps: int,
    guidance_scale: float,
    seed: int,
):
    if isinstance(source_video, dict):
        source_video = source_video.get("path")
    if not source_video:
        raise gr.Error("Please upload a source video.")
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter an edit prompt.")
    max_frames = int(max_frames)
    max_pixels = int(max_pixels)
    steps = int(steps)
    seed = int(seed)

    source_frames = load_video_frames(source_video, max_frames=max_frames, max_pixels=max_pixels)
    if len(source_frames) == 0:
        raise gr.Error("Could not read frames from the uploaded video.")

    ref = None
    if ref_image and os.path.exists(ref_image):
        ref = [Image.open(ref_image).convert("RGB")]

    pipe, device = load_pipeline(model_id)
    height, width = source_frames[0].size[1], source_frames[0].size[0]

    result = pipe(
        prompt=prompt.strip(),
        source_video=source_frames,
        ref_image=ref,
        height=height,
        width=width,
        num_frames=min(len(source_frames), max_frames),
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        seed=seed,
        tiled=True,
    )
    edited_frames = normalize_video_output(result)

    tmp_dir = tempfile.mkdtemp(prefix="kiwi_edit_")
    edited_path = os.path.join(tmp_dir, "edited.mp4")
    side_by_side_path = os.path.join(tmp_dir, "compare.mp4")
    export_to_video(edited_frames, edited_path, fps=15)

    compare_frames = concat_frames(source_frames, edited_frames)
    if compare_frames:
        export_to_video(compare_frames, side_by_side_path, fps=15)
    else:
        side_by_side_path = None

    status = (
        f"Done on {device}. Frames: {len(source_frames)}. "
        f"Resolution: {source_frames[0].width}x{source_frames[0].height}."
    )
    if not device.startswith("cuda"):
        status += " Running on CPU can be very slow."
    return edited_path, side_by_side_path, status


with gr.Blocks(title="Kiwi-Edit Diffusers Demo") as demo:
    gr.Markdown(
        "# Kiwi-Edit Diffusers (Gradio)\n"
        "Upload a video, enter an edit instruction, and optionally provide a reference image."
    )
    with gr.Row():
        with gr.Column():
            source_video = gr.Video(label="Source Video")
            prompt = gr.Textbox(
                label="Edit Prompt",
                lines=3,
                placeholder="Example: Replace the red car with a blue car while keeping motion consistent.",
            )
            ref_image = gr.Image(type="filepath", label="Reference Image (Optional)")
            model_id = gr.Dropdown(
                choices=MODEL_CHOICES,
                value=DEFAULT_MODEL,
                label="Model",
            )
            max_frames = gr.Slider(8, 81, value=81, step=1, label="Max Frames")
            max_pixels = gr.Slider(262144, 921600, value=720 * 1280, step=16384, label="Max Pixels")
            steps = gr.Slider(10, 80, value=50, step=1, label="Inference Steps")
            # guidance_scale = gr.Slider(1.0, 10.0, value=5.0, step=0.5, label="Guidance Scale")
            seed = gr.Number(value=0, precision=0, label="Seed")
            run_btn = gr.Button("Run Edit", variant="primary")
        with gr.Column():
            edited_video = gr.Video(label="Edited Video")
            comparison_video = gr.Video(label="Side-by-Side (Source | Edited)")
            status = gr.Textbox(label="Status", interactive=False)

    run_btn.click(
        fn=run_edit,
        inputs=[source_video, prompt, ref_image, model_id, max_frames, max_pixels, steps, 1.0, seed],
        outputs=[edited_video, comparison_video, status],
    )


if __name__ == "__main__":
    demo.queue().launch()
