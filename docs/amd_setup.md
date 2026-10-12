# AMD MI300X inference setup — execution pending

Documentation checked October 12, 2026. These are setup instructions, not evidence of a completed deployment. No AMD instance or real inference was available during local testing. The precise cloud image, driver, container digest and model revision must be recorded when tested together.

## Account and instance

Join the AMD AI Developer Program and confirm your cloud invitation/credits before creating resources. Availability and credit approval vary. In the cloud console select an MI300X GPU plan and a compatible ROCm Linux image, add your SSH public key, then create the VM. Retain the private key locally. Follow the provider’s exact SSH username/IP instructions. Confirm billing terms before provisioning. [AMD cloud access](https://www.amd.com/en/developer/resources/cloud-access.html) · [AMD getting started](https://www.amd.com/pt/developer/resources/technical-articles/2025/how-to-get-started-on-the-amd-developer-cloud-.html)

## ROCm and vLLM environment

Use the provider’s supported driver image. Upstream vLLM documents Linux, MI300 support and ROCm requirements; the container’s PyTorch/ROCm build must match the host driver compatibility matrix. Prefer the official ROCm container. `latest` below is a documented stable alias, not a reproducible version pin: record and reuse the pulled digest after verification. Do not reuse old CUDA or Radeon-specific examples. [vLLM GPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)

On the remote Linux machine, with Docker already installed by the provider:

```bash
docker pull vllm/vllm-openai-rocm:latest
docker image inspect vllm/vllm-openai-rocm:latest --format '{{index .RepoDigests 0}}'
read -rsp 'Private inference API key: ' VLLM_API_KEY; echo
export VLLM_API_KEY
docker run -d --name specguard-vllm \
  --group-add=video --device /dev/kfd --device /dev/dri \
  --ipc=host \
  -p 127.0.0.1:8000:8000 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e VLLM_API_KEY \
  vllm/vllm-openai-rocm:latest \
  --model Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000 \
  --dtype bfloat16 --max-model-len 16384
docker logs -f specguard-vllm
```

The service listens inside the container, with only host loopback port 8000 published. Device access and group membership are environment-dependent; if startup fails, compare the current upstream container instructions with the provider’s policy rather than disabling isolation indiscriminately. No privileged container is required by this example. The server downloads model weights into the mounted cache on first startup. Review the [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), disk requirements and model license before downloading. Qwen2.5 compatibility with the selected container still needs an actual launch test.

## Verify the API locally on the VM

```bash
curl --fail http://127.0.0.1:8000/v1/models \
  -H "Authorization: Bearer $VLLM_API_KEY"
curl --fail http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer $VLLM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"Return JSON with quantity equal to 500."}],"response_format":{"type":"json_object"},"max_tokens":128,"temperature":0}'
```

Check the listed model ID and valid JSON output. API-key authentication alone does not protect every vLLM route. Keep the port private; do not open it publicly. [vLLM API and authentication limitations](https://docs.vllm.ai/en/stable/serving/online_serving/openai_compatible_server/)

## Connect Windows securely

In a separate PowerShell terminal replace the key path, username and IP with the provider’s values:

```powershell
ssh -N -L 127.0.0.1:8000:127.0.0.1:8000 -i C:\path\to\private-key user@GPU_IP
```

Keep the terminal open. Copy `.env.example` to `.env` in the project. Set `SPECGUARD_MODE=live`, `VLLM_BASE_URL=http://127.0.0.1:8000/v1`, `VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct`, your private `VLLM_API_KEY`, and `REQUEST_TIMEOUT=60`. Start Streamlit and use Check model connection, then extract the synthetic documents and compare requirements. A successful model-list check verifies connectivity, not actual generation or AMD hardware.

## Capture real evidence and timings

With AMD SMI installed by the provider:

```bash
amd-smi version
amd-smi list
amd-smi static
amd-smi metric
amd-smi monitor --watch 1 --iterations 30
docker logs specguard-vllm
```

The AMD SMI commands report hardware and utilization; supported metrics depend on the driver/device. Consult `amd-smi --help` if the installed release differs. Capture telemetry while submitting an actual application request. [AMD SMI CLI](https://rocm.docs.amd.com/projects/amdsmi/en/latest/how-to/amdsmi-cli-tool.html)

Run locally:

```powershell
.\.venv\Scripts\python scripts/evaluate.py --mode live --output results/local_amd_evaluation.json
```

Retain model/container revisions, timestamps, hardware output, redacted server logs and the exported analysis showing live facts consumed by reconciliation. `processing_seconds` is pipeline wall time. `inference_request_seconds` measures client HTTP round trips including network, queueing and generation; it is not pure GPU kernel time or tokens/second. Demo values have no GPU interpretation. Review outputs for secrets before publishing evidence.

AMD integration is complete only after real GPU serving, actual structured output received by Streamlit, consumption by reconciliation, and verifiable execution evidence. It is currently incomplete.

## Stop unused resources

Stop only the project’s container with `docker stop specguard-vllm`; remove that stopped container with `docker rm specguard-vllm` when no longer needed. Save required evidence first. In the cloud console stop or destroy the identified VM according to the provider’s instructions and check for separately billed disks/IPs. Confirm the billing/resource view shows the intended resources released; container shutdown alone does not end instance charges. No cloud resources are deleted automatically by this repository.
