<h1><img src="https://github.com/linyq17/linyq17.github.io/blob/main/Kiwi-Edit/images/logo.png?raw=true" alt="Logo" width="30">
<span style="color: #6fa8dc;">K</span><span style="color: #6fb051;">i</span><span style="color: #e06766;">w</span><span style="color: #f6b26b;">i</span>-Edit: Versatile Video Editing via Instruction and Reference Guidance
</h1>
<p align="center">
  🌐 <a href="https://showlab.github.io/Kiwi-Edit">Project Page</a>&nbsp | 📑 <a href="#quick-start">Paper</a>&nbsp |  🤗 <a href="https://huggingface.co/collections/linyq/kiwi-edit">Models(🧨)</a> | 🤗 <a href="https://huggingface.co/datasets/linyq/kiwi_edit_training_data">Datasets</a>
</p>

Kiwi-Edit is a versatile video editing framework bulid upon on mllm encoder and video dit for:
- instruction video editing
- reference image + instruction video editing


## Quick Start

**Environment Requirements**

- Python 3.10 + CUDA 12.8 environment
- PyTorch==2.7, Accelerate
- For training: DeepSpeed, FlashAttention

### Full Environment Installation

**1) Prepare environment and base weights:**

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

All training metadata uses CSV, we provide demo data in the repo:

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


### Evaluation
For benchmark inferece example:
```bash
python infer.py \
  --ckpt_path path_to_ckpt \
  --bench openve \ # or refvie
  --max_frame 81 \
  --max_pixels 921600 \
  --save_dir ./infer_results/exp_name/
```
For score evaluation see `eval_openve_gemini.py` and `eval_refvie_gemini.py`. 

Example:

```bash
python eval_openve_gemini.py --video_paths path_to_videos
```

### Additional Notes

- Review and secure API key handling before running Gemini-based evaluation scripts.
- For Diffusers conversion, see `utils/convert_diffusers/README.md`.
- Some scripts include cluster-specific paths / tmux snippets; adapt them for your environment.
- Default benchmark paths in inference scripts assume datasets are under `./benchmark/...`.
- For debugging memory issues, reduce `--max_frame` and/or `--max_pixels`.

## Acknowledgements

Kiwi-Edit builds on training framework [ModelScope DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio), open-sourced datasets [Ditto-1M](https://huggingface.co/datasets/QingyanBai/Ditto-1M/tree/main/videos/source), [OpenVE-3M](https://huggingface.co/datasets/Lewandofski/OpenVE-3M), [ReCo](https://huggingface.co/datasets/HiDream-ai/ReCo-Data/tree/main), reward model [EditScore](https://github.com/VectorSpaceLab/EditScore) and image generation model [Qwen-Image-Edit](https://huggingface.co/Qwen/Qwen-Image-Edit-2511).

## Citation

If you use our code in your work, please cite [our paper]():

```bibtex
@article{
}
```