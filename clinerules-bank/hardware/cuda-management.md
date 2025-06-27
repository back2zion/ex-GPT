# CUDA Environment Management Guidelines

## Overview
Comprehensive guidelines for managing CUDA environments in the ex-GPT project, addressing driver compatibility, version management, and optimization for H100 GPU infrastructure at Korea Expressway Corporation.

## CUDA Version Requirements and Compatibility

### Current Environment Analysis
```bash
# Check current CUDA installation
nvidia-smi
nvcc --version
python -c "import torch; print(f'PyTorch CUDA: {torch.version.cuda}')"

# Check driver compatibility
cat /proc/driver/nvidia/version
modinfo nvidia | grep version
```

### Version Compatibility Matrix
```python
CUDA_COMPATIBILITY_MATRIX = {
    "h100": {
        "minimum_driver": "525.60.13",
        "recommended_driver": "535.129.03",
        "required_for_qwen3": "550.54.15",
        "optimal_for_qwen3": "570.47.03"
    },
    "cuda_versions": {
        "11.8": {
            "driver_min": "520.61.05",
            "pytorch_support": "2.0.0",
            "vllm_support": "0.2.0"
        },
        "12.1": {
            "driver_min": "530.30.02",
            "pytorch_support": "2.1.0",
            "vllm_support": "0.3.0"
        },
        "12.4": {
            "driver_min": "550.54.15",
            "pytorch_support": "2.3.0",
            "vllm_support": "0.4.0"
        }
    }
}
```

### Environment Validation Script
```python
import subprocess
import re
from packaging import version
from typing import Dict, List, Tuple
import torch

class CUDAEnvironmentValidator:
    def __init__(self):
        self.compatibility_matrix = CUDA_COMPATIBILITY_MATRIX
        
    def validate_environment(self) -> Dict:
        """Comprehensive CUDA environment validation"""
        
        results = {
            "nvidia_driver": self._check_nvidia_driver(),
            "cuda_runtime": self._check_cuda_runtime(),
            "pytorch_cuda": self._check_pytorch_cuda(),
            "gpu_compatibility": self._check_gpu_compatibility(),
            "recommendations": []
        }
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    def _check_nvidia_driver(self) -> Dict:
        """Check NVIDIA driver version and compatibility"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode != 0:
                return {"status": "error", "message": "nvidia-smi not found"}
            
            # Parse driver version
            driver_match = re.search(r'Driver Version: (\d+\.\d+\.\d+)', result.stdout)
            if driver_match:
                driver_version = driver_match.group(1)
                
                # Check H100 compatibility
                h100_requirements = self.compatibility_matrix["h100"]
                min_version = h100_requirements["minimum_driver"]
                rec_version = h100_requirements["recommended_driver"]
                qwen3_version = h100_requirements["required_for_qwen3"]
                
                status = "compatible"
                if version.parse(driver_version) < version.parse(min_version):
                    status = "incompatible"
                elif version.parse(driver_version) < version.parse(rec_version):
                    status = "needs_update"
                elif version.parse(driver_version) >= version.parse(qwen3_version):
                    status = "optimal"
                
                return {
                    "status": status,
                    "version": driver_version,
                    "minimum_required": min_version,
                    "recommended": rec_version,
                    "qwen3_required": qwen3_version
                }
            
            return {"status": "error", "message": "Could not parse driver version"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_gpu_memory_info(self) -> List[Dict]:
        """Get detailed GPU memory information"""
        try:
            memory_info = []
            for i in range(torch.cuda.device_count()):
                torch.cuda.set_device(i)
                total_memory = torch.cuda.get_device_properties(i).total_memory
                allocated = torch.cuda.memory_allocated(i)
                cached = torch.cuda.memory_reserved(i)
                
                memory_info.append({
                    "device_id": i,
                    "total_gb": total_memory / 1024**3,
                    "allocated_gb": allocated / 1024**3,
                    "cached_gb": cached / 1024**3,
                    "free_gb": (total_memory - allocated) / 1024**3,
                    "utilization": allocated / total_memory * 100
                })
            
            return memory_info
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        # Driver recommendations
        driver_info = results.get("nvidia_driver", {})
        if driver_info.get("status") == "incompatible":
            recommendations.append(
                f"CRITICAL: Update NVIDIA driver from {driver_info.get('version')} "
                f"to at least {driver_info.get('minimum_required')} for H100 compatibility"
            )
        elif driver_info.get("status") == "needs_update":
            recommendations.append(
                f"UPDATE RECOMMENDED: Current driver {driver_info.get('version')} "
                f"should be updated to {driver_info.get('qwen3_required')} for QWen3 support"
            )
        
        # CUDA recommendations
        cuda_info = results.get("cuda_runtime", {})
        pytorch_info = results.get("pytorch_cuda", {})
        
        if cuda_info.get("status") == "error":
            recommendations.append("INSTALL: CUDA runtime not found. Install CUDA toolkit")
        
        if pytorch_info.get("status") == "error":
            recommendations.append("INSTALL: PyTorch CUDA support not available. Reinstall PyTorch with CUDA")
        
        # GPU recommendations
        gpu_info = results.get("gpu_compatibility", {})
        if gpu_info.get("h100_count", 0) == 0:
            recommendations.append("WARNING: No H100 GPUs detected. Verify hardware configuration")
        
        return recommendations
```

## Driver Update Procedures

### Safe Driver Update Process
```bash
#!/bin/bash
# H100 Driver Update Script for ex-GPT Project

# Pre-update checks
echo "=== Pre-update System Check ==="
nvidia-smi
lsmod | grep nvidia
systemctl status nvidia-persistenced

# Create backup of current configuration
echo "=== Creating Configuration Backup ==="
cp /etc/X11/xorg.conf /etc/X11/xorg.conf.backup.$(date +%Y%m%d)
nvidia-settings --query all > nvidia-settings-backup-$(date +%Y%m%d).txt

# Stop services that might interfere
echo "=== Stopping Related Services ==="
sudo systemctl stop nvidia-persistenced
sudo systemctl stop gdm3  # or lightdm/sddm depending on display manager

# Remove old driver (if needed)
echo "=== Removing Old Driver ==="
sudo apt purge nvidia-* -y
sudo apt autoremove -y

# Download and install new driver
echo "=== Installing New Driver ==="
DRIVER_VERSION="570.47.03"
wget https://us.download.nvidia.com/XFree86/Linux-x86_64/$DRIVER_VERSION/NVIDIA-Linux-x86_64-$DRIVER_VERSION.run

chmod +x NVIDIA-Linux-x86_64-$DRIVER_VERSION.run
sudo ./NVIDIA-Linux-x86_64-$DRIVER_VERSION.run --ui=none --no-questions --accept-license

# Restart services
echo "=== Restarting Services ==="
sudo systemctl start nvidia-persistenced
sudo systemctl start gdm3

# Verify installation
echo "=== Post-installation Verification ==="
nvidia-smi
nvidia-ml-py --version
```

### Driver Rollback Procedure
```bash
#!/bin/bash
# Driver Rollback Script

echo "=== Emergency Driver Rollback ==="

# Use DKMS to rebuild previous driver if available
sudo dkms status | grep nvidia

# Or reinstall from package manager
sudo apt update
sudo apt install nvidia-driver-535 -y

# Reconfigure
sudo nvidia-xconfig
sudo systemctl restart nvidia-persistenced
sudo reboot
```

## CUDA Environment Setup

### Multi-Version CUDA Management
```bash
# Install CUDA using conda for better version management
conda create -n ex-gpt-cuda12.4 python=3.10
conda activate ex-gpt-cuda12.4

# Install specific CUDA version
conda install cudatoolkit=12.4 -c conda-forge
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

# Verify installation
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

### Environment Variables Configuration
```bash
# ~/.bashrc or project-specific environment
export CUDA_HOME=/usr/local/cuda-12.4
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# For multiple CUDA versions
export CUDA_11_8_HOME=/usr/local/cuda-11.8
export CUDA_12_4_HOME=/usr/local/cuda-12.4
export CUDA_HOME=$CUDA_12_4_HOME  # Set default

# vLLM specific optimizations
export VLLM_USE_MODELSCOPE=True
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7  # All H100 GPUs
```

## Performance Optimization

### GPU Performance Monitoring
```python
import subprocess
import json
import time
from typing import Dict, List

class GPUPerformanceMonitor:
    def __init__(self, monitoring_interval: int = 5):
        self.monitoring_interval = monitoring_interval
        self.metrics_history = []
    
    def get_gpu_metrics(self) -> Dict:
        """Get comprehensive GPU metrics"""
        try:
            # Use nvidia-ml-py for detailed metrics
            import pynvml
            
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            metrics = {
                "timestamp": time.time(),
                "devices": []
            }
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Basic info
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                
                # Memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Temperature
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                # Power usage
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                
                # Utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Clock speeds
                graphics_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                memory_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                
                device_metrics = {
                    "device_id": i,
                    "name": name,
                    "memory": {
                        "total_gb": mem_info.total / 1024**3,
                        "used_gb": mem_info.used / 1024**3,
                        "free_gb": mem_info.free / 1024**3,
                        "utilization_percent": (mem_info.used / mem_info.total) * 100
                    },
                    "temperature_c": temp,
                    "power_watts": power,
                    "utilization": {
                        "gpu_percent": util.gpu,
                        "memory_percent": util.memory
                    },
                    "clocks": {
                        "graphics_mhz": graphics_clock,
                        "memory_mhz": memory_clock
                    }
                }
                
                metrics["devices"].append(device_metrics)
            
            return metrics
            
        except ImportError:
            # Fallback to nvidia-smi if pynvml not available
            return self._get_metrics_nvidia_smi()
        except Exception as e:
            return {"error": str(e)}
    
    def _get_metrics_nvidia_smi(self) -> Dict:
        """Fallback method using nvidia-smi"""
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free,temperature.gpu,power.draw,utilization.gpu,utilization.memory",
                "--format=csv,noheader,nounits"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": "nvidia-smi failed"}
            
            metrics = {
                "timestamp": time.time(),
                "devices": []
            }
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = [p.strip() for p in line.split(',')]
                    device_metrics = {
                        "device_id": int(parts[0]),
                        "name": parts[1],
                        "memory": {
                            "total_gb": float(parts[2]) / 1024,
                            "used_gb": float(parts[3]) / 1024,
                            "free_gb": float(parts[4]) / 1024,
                            "utilization_percent": (float(parts[3]) / float(parts[2])) * 100
                        },
                        "temperature_c": float(parts[5]),
                        "power_watts": float(parts[6]),
                        "utilization": {
                            "gpu_percent": float(parts[7]),
                            "memory_percent": float(parts[8])
                        }
                    }
                    metrics["devices"].append(device_metrics)
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def monitor_continuous(self, duration_minutes: int = 60):
        """Monitor GPU performance continuously"""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            metrics = self.get_gpu_metrics()
            if "error" not in metrics:
                self.metrics_history.append(metrics)
            
            time.sleep(self.monitoring_interval)
        
        return self.metrics_history
    
    def get_performance_summary(self) -> Dict:
        """Generate performance summary from collected metrics"""
        if not self.metrics_history:
            return {"error": "No metrics collected"}
        
        device_count = len(self.metrics_history[0]["devices"])
        summary = {
            "monitoring_duration_minutes": len(self.metrics_history) * self.monitoring_interval / 60,
            "devices": []
        }
        
        for device_id in range(device_count):
            device_metrics = []
            for snapshot in self.metrics_history:
                device_metrics.append(snapshot["devices"][device_id])
            
            # Calculate statistics
            gpu_utils = [d["utilization"]["gpu_percent"] for d in device_metrics]
            mem_utils = [d["memory"]["utilization_percent"] for d in device_metrics]
            temps = [d["temperature_c"] for d in device_metrics]
            powers = [d["power_watts"] for d in device_metrics]
            
            device_summary = {
                "device_id": device_id,
                "name": device_metrics[0]["name"],
                "gpu_utilization": {
                    "average": sum(gpu_utils) / len(gpu_utils),
                    "max": max(gpu_utils),
                    "min": min(gpu_utils)
                },
                "memory_utilization": {
                    "average": sum(mem_utils) / len(mem_utils),
                    "max": max(mem_utils),
                    "min": min(mem_utils)
                },
                "temperature": {
                    "average": sum(temps) / len(temps),
                    "max": max(temps),
                    "min": min(temps)
                },
                "power": {
                    "average": sum(powers) / len(powers),
                    "max": max(powers),
                    "min": min(powers)
                }
            }
            
            summary["devices"].append(device_summary)
        
        return summary
```

### CUDA Memory Management
```python
import torch
import gc
from typing import Optional

class CUDAMemoryManager:
    def __init__(self):
        self.memory_snapshots = []
    
    def optimize_memory_usage(self):
        """Optimize CUDA memory usage"""
        
        # Clear PyTorch cache
        torch.cuda.empty_cache()
        
        # Force garbage collection
        gc.collect()
        
        # Set memory growth strategy
        if hasattr(torch.cuda, 'set_memory_strategy'):
            torch.cuda.set_memory_strategy('expandable_segments')
    
    def get_memory_status(self) -> Dict:
        """Get detailed memory status for all GPUs"""
        
        if not torch.cuda.is_available():
            return {"error": "CUDA not available"}
        
        status = {
            "device_count": torch.cuda.device_count(),
            "devices": []
        }
        
        for i in range(torch.cuda.device_count()):
            torch.cuda.set_device(i)
            
            props = torch.cuda.get_device_properties(i)
            allocated = torch.cuda.memory_allocated(i)
            cached = torch.cuda.memory_reserved(i)
            
            device_status = {
                "device_id": i,
                "name": props.name,
                "total_memory_gb": props.total_memory / 1024**3,
                "allocated_gb": allocated / 1024**3,
                "cached_gb": cached / 1024**3,
                "free_gb": (props.total_memory - allocated) / 1024**3,
                "utilization_percent": (allocated / props.total_memory) * 100,
                "compute_capability": f"{props.major}.{props.minor}",
                "multiprocessor_count": props.multi_processor_count
            }
            
            status["devices"].append(device_status)
        
        return status
    
    def monitor_memory_usage(self, operation_name: str = ""):
        """Context manager for monitoring memory usage during operations"""
        
        class MemoryMonitor:
            def __init__(self, manager, name):
                self.manager = manager
                self.name = name
                self.start_memory = None
                self.end_memory = None
            
            def __enter__(self):
                self.start_memory = self.manager.get_memory_status()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.end_memory = self.manager.get_memory_status()
                self.manager._log_memory_usage(self.name, self.start_memory, self.end_memory)
        
        return MemoryMonitor(self, operation_name)
    
    def _log_memory_usage(self, operation: str, start: Dict, end: Dict):
        """Log memory usage differences"""
        
        print(f"\n=== Memory Usage Report: {operation} ===")
        
        for i, (start_dev, end_dev) in enumerate(zip(start["devices"], end["devices"])):
            allocated_diff = end_dev["allocated_gb"] - start_dev["allocated_gb"]
            cached_diff = end_dev["cached_gb"] - start_dev["cached_gb"]
            
            print(f"GPU {i} ({start_dev['name']}):")
            print(f"  Allocated: {start_dev['allocated_gb']:.2f}GB -> {end_dev['allocated_gb']:.2f}GB ({allocated_diff:+.2f}GB)")
            print(f"  Cached: {start_dev['cached_gb']:.2f}GB -> {end_dev['cached_gb']:.2f}GB ({cached_diff:+.2f}GB)")
            print(f"  Utilization: {start_dev['utilization_percent']:.1f}% -> {end_dev['utilization_percent']:.1f}%")
```

## Troubleshooting and Diagnostics

### Common Issues and Solutions
```python
class CUDATroubleshooter:
    def __init__(self):
        self.common_issues = {
            "driver_mismatch": {
                "symptoms": ["CUDA version mismatch", "RuntimeError: CUDA error"],
                "solutions": [
                    "Update NVIDIA driver to compatible version",
                    "Reinstall PyTorch with correct CUDA version",
                    "Check CUDA_HOME environment variable"
                ]
            },
            "memory_fragmentation": {
                "symptoms": ["CUDA out of memory", "Memory allocation failed"],
                "solutions": [
                    "torch.cuda.empty_cache()",
                    "Reduce batch size",
                    "Enable gradient checkpointing",
                    "Use mixed precision training"
                ]
            },
            "multi_gpu_issues": {
                "symptoms": ["Tensor parallel errors", "GPU communication failures"],
                "solutions": [
                    "Check NCCL installation",
                    "Verify GPU topology",
                    "Set CUDA_VISIBLE_DEVICES correctly",
                    "Check PCIe connectivity"
                ]
            }
        }
    
    def diagnose_issue(self, error_message: str) -> Dict:
        """Diagnose CUDA-related issues based on error message"""
        
        recommendations = []
        
        for issue_type, details in self.common_issues.items():
            for symptom in details["symptoms"]:
                if symptom.lower() in error_message.lower():
                    recommendations.extend(details["solutions"])
        
        return {
            "error_message": error_message,
            "recommended_solutions": list(set(recommendations)),
            "diagnostic_commands": [
                "nvidia-smi",
                "nvcc --version",
                "python -c 'import torch; print(torch.cuda.is_available())'",
                "python -c 'import torch; print(torch.version.cuda)'"
            ]
        }
    
    def run_comprehensive_diagnostic(self) -> Dict:
        """Run comprehensive CUDA environment diagnostic"""
        
        validator = CUDAEnvironmentValidator()
        monitor = GPUPerformanceMonitor()
        memory_manager = CUDAMemoryManager()
        
        diagnostic_results = {
            "environment_validation": validator.validate_environment(),
            "gpu_metrics": monitor.get_gpu_metrics(),
            "memory_status": memory_manager.get_memory_status(),
            "system_info": self._get_system_info()
        }
        
        return diagnostic_results
    
    def _get_system_info(self) -> Dict:
        """Get relevant system information"""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "total_memory_gb": psutil.virtual_memory().total / 1024**3,
                "available_memory_gb": psutil.virtual_memory().available / 1024**3
            }
        except ImportError:
            return {"error": "psutil not available"}
```
