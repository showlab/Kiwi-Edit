<h1><img src="webpage/images/logo.png" alt="Logo" width="30">
<span style="color: #6fa8dc;">K</span><span style="color: #6fb051;">i</span><span style="color: #e06766;">w</span><span style="color: #f6b26b;">i</span>-Edit: Versatile Video Editing via Instruction and Reference Guidance
</h1>
<p align="center">
  🌐 <a href="https://showlab.github.io/Kiwi-Edit">Project Page</a>&nbsp | 📑 <a href=https://arxiv.org/abs/2603.02175>Paper</a>&nbsp |  🤗 <a href="https://huggingface.co/collections/linyq/kiwi-edit">Models(🧨)</a> | 🤗 <a href="https://huggingface.co/datasets/linyq/kiwi_edit_training_data">Datasets</a>
</p>

Kiwi-Edit is a versatile video editing framework built on an MLLM encoder and a video DiT for:
- instruction video editing
- reference image + instruction video editing

## Visualization Demos

<details open>
  <summary><strong>Style</strong></summary>
  <p align="center"><img src="webpage/gifs/0007_global_style_Apply_the_dynamic_ae_concat.gif" alt="Style example gif" height="480"></p>
  <p align="center"><em>"Apply the dynamic aesthetic of abstract art to this video."</em></p>
</details>

<details>
  <summary><strong>Replace</strong></summary>
  <p align="center"><img src="webpage/gifs/0083_local_change_Replace_the_sofa_wit_70_concat.gif" alt="Replace example gif" height="320"></p>
  <p align="center"><em>"Replace the sofa with a classic brown leather sofa with visible stitching."</em></p>
</details>

<details>
  <summary><strong>Add</strong></summary>
  <p align="center"><img src="webpage/gifs/0095_local_change_Add_a_classic_brown_concat.gif" alt="Add example gif" height="320"></p>
  <p align="center"><em>"Add a classic brown fedora hat to the boy's head."</em></p>
</details>

<details>
  <summary><strong>Remove</strong></summary>
  <p align="center"><img src="webpage/gifs/0191_local_remove_Remove_the_person_we_concat.gif" alt="Remove example gif" height="480"></p>
  <p align="center"><em>"Remove the person wearing a light blue shirt and dark pants from the entire video sequence."</em></p>
</details>

<details>
  <summary><strong>Background Replace</strong></summary>
  <p align="center"><img src="webpage/gifs/0145_background_change_Replace_the_backgrou_concat.gif" alt="Background replace example gif" height="320"></p>
  <p align="center"><em>"Replace the background with a lively urban garden scene during winter."</em></p>
</details>

<details>
  <summary><strong>Subject Reference</strong></summary>
  <table align="center">
    <tr align="center">
      <td align="center"><img src="webpage/images/41_shape_heart_sunglasses_1328_1328_1.png" alt="Reference image" height="224"></td>
      <td align="center"><img src="webpage/gifs/0125_background_change_Replace_the_backgrou_concat.gif" alt="Subject reference example gif" height="480"></td>
    </tr>
  </table>
  <p align="center"><em>"Add a pair of iconic red heart-shaped sunglasses to the girl's face."</em></p>
</details>

<details>
  <summary><strong>Background Reference</strong></summary>
  <table align="center">
    <tr align="center">
      <td align="center"><img src="webpage/images/0_mountain_ink_1664_928_0.png" alt="Reference image" height="128"></td>
      <td align="center"><img src="webpage/gifs/1_Replace_th_gym-ball_concat.gif" alt="Background reference example gif" height="320"></td>
    </tr>
  </table>
  <p align="center"><em>"Replace the background with a Chinese ink painting, featuring a large golden mountain peak rising above swirling clouds."</em></p>
</details>

## News

- [2026-03-03] Code and model released.

## Quick Start

**Environment Requirements**

- Python 3.10 + CUDA 12.8 environment
- PyTorch==2.7, Accelerate
- For training: DeepSpeed, FlashAttention

### Full Environment Installation

**1) Prepare environment and base weights:**
```bash
# Create conda environment
conda create -n diffsynth python=3.10 -y
conda activate diffsynth
# Install PyTorch 2.7 with CUDA
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128
pip install -e .
conda install mpi4py -y
pip install deepspeed
pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu12torch2.7cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
pip install transformers==4.57.0 huggingface-hub==0.34 wandb
# Prepare the pretrained video dit
mkdir -p models/Wan-AI/
# Please login first
hf download Wan-AI/Wan2.2-TI2V-5B --local-dir ./models/Wan-AI/Wan2.2-TI2V-5B
```

or

```bash
bash install_full_env.sh
```

**2) Run a quick test on demo video:**

```bash
python demo.py \
  --ckpt_path path_to_checkpoint \
  --video_path ./demo_data/video/source/0005e4ad9f49814db1d3f2296b911abf.mp4 \
  --prompt "Remove the monkey." \
  --save_path ./output/demo_output.mp4
```
### Diffusers Inference Environment Installation
**1) Prepare environment:**

```bash
# Create conda environment
conda create -n diffusers python=3.10 -y
conda activate diffusers
# Install PyTorch 2.7 with CUDA
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128
pip install diffusers decord einops accelerate transformers==4.57.0 opencv-python av
```

or

```bash
bash install_diffusers_env.sh
```

**2) Run a quick test on demo video:**

```bash
python diffusers_demo.py \
    --video_path ./demo_data/video/source/0005e4ad9f49814db1d3f2296b911abf.mp4 \
    --prompt "Remove the monkey." \
    --save_path output.mp4 --model_path linyq/kiwi-edit-5b-instruct-only-diffusers
```

## Training and Evaluation

### Dataset Format

All training metadata uses CSV; we provide demo data in the repo:

- Image stage: `src_video`, `tgt_video`, `prompt`  
  Example: `demo_data/image_demo_training_set.csv`
- Video stage: `src_video`, `tgt_video`, `prompt`  
  Example: `demo_data/video_demo_training_set.csv`
- Reference-video stage: `src_video`, `tgt_video`, `ref_image`, `prompt`  
  Example: `demo_data/video_ref_demo_training_set.csv`

For full data training, please refer to [DATASET.md](DATASET.md).

### Training

Use the provided scripts in `scripts/`. Example:

```bash
bash scripts/run_wan2.2_ti2v_5b_qwen25vl_3b_stage3_img_vid_refvid_720x1280_81f.sh
```

Training scripts, key parameters, and placeholder links:

| Script | Model Size | Training Stage (Data) | Max Pixels | Frames | LR | Steps | Model Weights |
| - | - | - | - | - | - | - | - |
| [link](scripts/run_wan2.2_ti2v_5b_qwen25vl_3b_stage1_img_1024x1024_1f.sh) | [Qwen2.5-VL-3B](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)+[Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) | Stage 1 (Image) | 1024x1024 | 1 | 1e-5 | 30K | [link](https://huggingface.co/linyq/wan2.2_ti2v_5b_qwen25vl_3b_stage1_img_only) |
| [link](scripts/run_wan2.2_ti2v_5b_qwen25vl_3b_stage2_img_vid_600x600_81f.sh) | [Qwen2.5-VL-3B](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)+[Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) | Stage 2 (Image + Video) | 600x600 | 81 | 1e-5 | 20K | [link](https://huggingface.co/linyq/wan2.2_ti2v_5b_qwen25vl_3b_stage2_img_vid_600x600_81f) |
| [link](scripts/run_wan2.2_ti2v_5b_qwen25vl_3b_stage2_img_vid_720x1280_81f.sh) | [Qwen2.5-VL-3B](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)+[Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) | Stage 2 (Image + Video) | 720x1280 | 81 | 1e-5 | 20K | [link](https://huggingface.co/linyq/wan2.2_ti2v_5b_qwen25vl_3b_stage2_img_vid_720x1280_81f) |
| [link](scripts/run_wan2.2_ti2v_5b_qwen25vl_3b_stage3_img_vid_refvid_720x1280_81f.sh) | [Qwen2.5-VL-3B](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)+[Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) | Stage 3 (Image + Video + Ref-Video) | 720x1280 | 81 | 5e-6 | 15K | [link](https://huggingface.co/linyq/wan2.2_ti2v_5b_qwen25vl_3b_stage3_img_vid_refvid_720x1280_81f) |
| [link](scripts/run_wan2.2_ti2v_5b_qwen25vl_3b_stage3_refvid_720x1280_81f.sh) | [Qwen2.5-VL-3B](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)+[Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) | Stage 3 (Ref-Video) | 720x1280 | 81 | 5e-6 | 30K | [link](https://huggingface.co/linyq/wan2.2_ti2v_5b_qwen25vl_3b_stage3_refvid_only_720x1280_81f_pad_first) |


### Evaluation
For benchmark inference example:
```bash
python infer.py \
  --ckpt_path path_to_ckpt \
  --bench openve \  # or refvie
  --max_frame 81 \
  --max_pixels 921600 \
  --save_dir ./infer_results/exp_name/
```
For score evaluation, see `eval_openve_gemini.py` and `eval_refvie_gemini.py`.

Example:

```bash
python eval_openve_gemini.py --video_paths path_to_videos
```

### Additional Notes

- Review and secure API key handling before running Gemini-based evaluation scripts.
- For Diffusers conversion, see `utils/convert_diffusers/README.md`.
- Default benchmark paths in inference scripts assume datasets are under `./benchmark/...`.

## Acknowledgements

Kiwi-Edit builds on training framework [ModelScope DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio), open-sourced datasets [Ditto-1M](https://huggingface.co/datasets/QingyanBai/Ditto-1M/tree/main/videos/source), [OpenVE-3M](https://huggingface.co/datasets/Lewandofski/OpenVE-3M), [ReCo](https://huggingface.co/datasets/HiDream-ai/ReCo-Data/tree/main), [GPT-Image-Edit-1.5M](https://huggingface.co/datasets/UCSC-VLAA/GPT-Image-Edit-1.5M), [NHR-Edit](https://huggingface.co/datasets/iitolstykh/NHR-Edit), reward model [EditScore](https://github.com/VectorSpaceLab/EditScore) and image generation model [Qwen-Image-Edit](https://huggingface.co/Qwen/Qwen-Image-Edit-2511).

## Citation

If you use our code in your work, please cite [our paper](https://arxiv.org/abs/2603.02175):

```bibtex
@misc{kiwiedit,
      title={Kiwi-Edit: Versatile Video Editing via Instruction and Reference Guidance}, 
      author={Yiqi Lin and Guoqiang Liang and Ziyun Zeng and Zechen Bai and Yanzhe Chen and Mike Zheng Shou},
      year={2026},
      eprint={2603.02175},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2603.02175}, 
}
```
