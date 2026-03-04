# import os
# import tempfile
# from typing import List, Optional, Sequence, Tuple, Union

# import gradio as gr
# import numpy as np
# import torch
# from PIL import Image
# from diffusers import DiffusionPipeline
# from diffusers.utils import export_to_video
# from torchvision.io import read_video

# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# DEFAULT_MODEL = "linyq/kiwi-edit-5b-instruct-reference-diffusers"
# MODEL_CHOICES = [
#     "linyq/kiwi-edit-5b-instruct-only-diffusers",
#     "linyq/kiwi-edit-5b-reference-only-diffusers",
#     "linyq/kiwi-edit-5b-instruct-reference-diffusers",
# ]

# _PIPELINE_CACHE = {}


# def _device_and_dtype() -> Tuple[str, torch.dtype]:
#     if torch.cuda.is_available():
#         # float16 is broadly supported on consumer GPUs in Spaces.
#         return "cuda:0", torch.float16
#     return "cpu", torch.float32


# def _safe_int(v: Union[int, float]) -> int:
#     return int(v)


# def _to_uint8_array(frame) -> np.ndarray:
#     if isinstance(frame, Image.Image):
#         return np.array(frame.convert("RGB"), dtype=np.uint8)

#     if isinstance(frame, np.ndarray):
#         arr = frame
#         if arr.dtype != np.uint8:
#             if arr.max() <= 1.0:
#                 arr = (arr * 255.0).clip(0, 255)
#             arr = arr.astype(np.uint8)
#         if arr.ndim == 3 and arr.shape[0] in (1, 3, 4) and arr.shape[-1] not in (1, 3, 4):
#             arr = np.transpose(arr, (1, 2, 0))
#         if arr.shape[-1] == 4:
#             arr = arr[..., :3]
#         return arr

#     if isinstance(frame, torch.Tensor):
#         t = frame.detach().cpu()
#         if t.ndim == 3 and t.shape[0] in (1, 3, 4):
#             t = t.permute(1, 2, 0)
#         arr = t.numpy()
#         return _to_uint8_array(arr)

#     raise TypeError(f"Unsupported frame type: {type(frame)}")


# def _normalize_pipeline_output(result) -> Sequence:
#     if isinstance(result, (list, tuple)):
#         return result[0] if isinstance(result, tuple) else result

#     if hasattr(result, "frames"):
#         frames = result.frames
#         if isinstance(frames, list) and frames and isinstance(frames[0], list):
#             return frames[0]
#         return frames

#     if hasattr(result, "videos"):
#         videos = result.videos
#         if isinstance(videos, list):
#             return videos[0] if videos else []
#         if isinstance(videos, torch.Tensor) and videos.ndim == 5:
#             return videos[0]
#         return videos

#     if isinstance(result, torch.Tensor) and result.ndim == 5:
#         return result[0]

#     return result


# def load_video_frames(video_path: str, max_frames: int, max_pixels: int) -> List[Image.Image]:
#     vframes, _, _ = read_video(video_path, pts_unit="sec")
#     frames: List[Image.Image] = []

#     for i in range(min(len(vframes), max_frames)):
#         img = Image.fromarray(vframes[i].numpy()).convert("RGB")
#         w, h = img.size
#         scale = min(1.0, (max_pixels / (w * h)) ** 0.5)
#         if scale < 1.0:
#             new_w = max((int(w * scale) // 16) * 16, 16)
#             new_h = max((int(h * scale) // 16) * 16, 16)
#             img = img.resize((new_w, new_h), Image.LANCZOS)
#         frames.append(img)

#     return frames


# def load_pipeline(model_id: str):
#     device, dtype = _device_and_dtype()
#     cache_key = (model_id, device, str(dtype))

#     if cache_key in _PIPELINE_CACHE:
#         return _PIPELINE_CACHE[cache_key], device

#     pipe = DiffusionPipeline.from_pretrained(model_id, trust_remote_code=True)
#     pipe.to(device, dtype=dtype)
#     _PIPELINE_CACHE[cache_key] = pipe
#     return pipe, device


# def make_side_by_side(source_frames: Sequence[Image.Image], edited_frames: Sequence) -> List[np.ndarray]:
#     if not source_frames or not edited_frames:
#         return []

#     n = min(len(source_frames), len(edited_frames))
#     compare = []
#     for i in range(n):
#         left = np.array(source_frames[i].convert("RGB"), dtype=np.uint8)
#         right = _to_uint8_array(edited_frames[i])

#         h = max(left.shape[0], right.shape[0])
#         w = left.shape[1] + right.shape[1]
#         canvas = np.zeros((h, w, 3), dtype=np.uint8)
#         canvas[: left.shape[0], : left.shape[1]] = left
#         canvas[: right.shape[0], left.shape[1] :] = right
#         compare.append(canvas)

#     return compare


# def run_edit(
#     source_video,
#     prompt: str,
#     ref_image: Optional[str],
#     model_id: str,
#     max_frames: int,
#     max_pixels: int,
#     steps: int,
#     guidance_scale: float,
#     seed: int,
# ):
#     if isinstance(source_video, dict):
#         source_video = source_video.get("path")

#     if not source_video:
#         raise gr.Error("Please upload a source video.")
#     if not prompt or not prompt.strip():
#         raise gr.Error("Please enter an edit prompt.")

#     max_frames = _safe_int(max_frames)
#     max_pixels = _safe_int(max_pixels)
#     steps = _safe_int(steps)
#     seed = _safe_int(seed)

#     source_frames = load_video_frames(source_video, max_frames=max_frames, max_pixels=max_pixels)
#     if not source_frames:
#         raise gr.Error("Could not read frames from this video.")

#     pipe, device = load_pipeline(model_id)

#     ref = None
#     if ref_image and os.path.exists(ref_image):
#         ref = [Image.open(ref_image).convert("RGB")]

#     height, width = source_frames[0].size[1], source_frames[0].size[0]

#     result = pipe(
#         prompt=prompt.strip(),
#         source_video=source_frames,
#         ref_image=ref,
#         height=height,
#         width=width,
#         num_frames=min(len(source_frames), max_frames),
#         num_inference_steps=steps,
#         guidance_scale=guidance_scale,
#         seed=seed,
#         tiled=True,
#     )

#     edited_frames_raw = _normalize_pipeline_output(result)
#     edited_frames = [_to_uint8_array(f) for f in edited_frames_raw]

#     out_dir = tempfile.mkdtemp(prefix="kiwi_edit_")
#     edited_path = os.path.join(out_dir, "edited.mp4")
#     compare_path = os.path.join(out_dir, "source_vs_edited.mp4")

#     export_to_video(edited_frames, edited_path, fps=15)

#     compare_frames = make_side_by_side(source_frames, edited_frames)
#     if compare_frames:
#         export_to_video(compare_frames, compare_path, fps=15)
#     else:
#         compare_path = None

#     status = f"Done on {device} | {len(source_frames)} frames | {width}x{height}"
#     if not device.startswith("cuda"):
#         status += " (CPU mode can be very slow)"

#     return edited_path, compare_path, status


# with gr.Blocks(title="Kiwi-Edit Diffusers Demo") as demo:
#     gr.Markdown(
#         "# Kiwi-Edit (Diffusers + Gradio)\n"
#         "Hugging Face Spaces style demo for video editing."
#     )

#     with gr.Row():
#         with gr.Column():
#             source_video = gr.Video(label="Source Video")
#             prompt = gr.Textbox(
#                 label="Edit Prompt",
#                 lines=3,
#                 placeholder="Example: Replace the red umbrella with a yellow umbrella while keeping motion consistent.",
#             )
#             ref_image = gr.Image(type="filepath", label="Reference Image (Optional)")
#             model_id = gr.Dropdown(MODEL_CHOICES, value=DEFAULT_MODEL, label="Model")
#             max_frames = gr.Slider(8, 81, value=81, step=1, label="Max Frames")
#             max_pixels = gr.Slider(262144, 921600, value=720 * 1280, step=16384, label="Max Pixels")
#             steps = gr.Slider(10, 80, value=50, step=1, label="Inference Steps")
#             guidance_scale = gr.Slider(1.0, 10.0, value=5.0, step=0.5, label="Guidance Scale")
#             seed = gr.Number(value=0, precision=0, label="Seed")
#             run_btn = gr.Button("Run Edit", variant="primary")

#         with gr.Column():
#             edited_video = gr.Video(label="Edited Video")
#             compare_video = gr.Video(label="Side-by-Side (Source | Edited)")
#             status = gr.Textbox(label="Status", interactive=False)

#     run_btn.click(
#         fn=run_edit,
#         inputs=[source_video, prompt, ref_image, model_id, max_frames, max_pixels, steps, guidance_scale, seed],
#         outputs=[edited_video, compare_video, status],
#     )


# if __name__ == "__main__":
#     demo.queue().launch(share=True)
import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
    api_name="predict"
)

demo.launch()
